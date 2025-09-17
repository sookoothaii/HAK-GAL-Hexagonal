#!/usr/bin/env python3
"""
HRM Training Pipeline for HAK-GAL HEXAGONAL
============================================
Trainiert das Hierarchical Reasoning Model mit Facts aus der Knowledge Base
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import sqlite3
import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedHRM(nn.Module):
    """
    Verbessertes HRM Model mit GRU und Attention
    """
    def __init__(self, vocab_size: int = 5000, embedding_dim: int = 128, 
                 hidden_dim: int = 256, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        
        # Embedding layers
        self.entity_embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.predicate_embedding = nn.Embedding(100, embedding_dim)  # Max 100 predicates
        
        # GRU for sequence processing
        self.gru = nn.GRU(
            embedding_dim * 2,  # entity + predicate
            hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(hidden_dim * 2, num_heads=4, batch_first=True)
        
        # Output layers
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, 1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, entities, predicates):
        # Embed inputs
        entity_emb = self.entity_embedding(entities)
        pred_emb = self.predicate_embedding(predicates)
        
        # Concatenate embeddings
        combined = torch.cat([entity_emb, pred_emb.unsqueeze(1).expand(-1, entity_emb.size(1), -1)], dim=-1)
        
        # GRU processing
        gru_out, _ = self.gru(combined)
        
        # Self-attention
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)
        
        # Global pooling
        pooled = torch.mean(attn_out, dim=1)
        
        # Classification
        x = self.dropout(pooled)
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        output = self.fc2(x)
        
        return self.sigmoid(output).squeeze(-1)


class FactDataset(Dataset):
    """
    Dataset für Knowledge Base Facts
    """
    def __init__(self, db_path: str, max_facts: int = 10000):
        self.facts = []
        self.labels = []
        self.vocab = {'<PAD>': 0, '<UNK>': 1}
        self.predicate_vocab = {'<UNK>': 0}
        
        # Load facts from SQLite
        self._load_facts(db_path, max_facts)
        
        # Generate positive and negative examples
        self._generate_training_data()
        
    def _load_facts(self, db_path: str, max_facts: int):
        """Load facts from SQLite database"""
        if not Path(db_path).exists():
            logger.error(f"Database not found: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT statement FROM facts LIMIT ?", (max_facts,))
            raw_facts = cursor.fetchall()
            
            for (statement,) in raw_facts:
                parsed = self._parse_fact(statement)
                if parsed:
                    self.facts.append(parsed)
                    
            logger.info(f"Loaded {len(self.facts)} facts from database")
            
        except Exception as e:
            logger.error(f"Error loading facts: {e}")
        finally:
            conn.close()
            
    def _parse_fact(self, statement: str) -> Optional[Dict]:
        """Parse fact into predicate and entities (supports multi-argument facts)"""
        # Pattern: Predicate(Entity1, Entity2, ...).
        pattern = r'^([A-Z][A-Za-z0-9_]*)\((.*?)\)\.$'
        match = re.match(pattern, statement)
        
        if match:
            predicate = match.group(1)
            entities_str = match.group(2)
            
            # Split entities (handle multi-argument facts)
            entities = [e.strip() for e in entities_str.split(',')]
            
            # Add to vocabularies
            if predicate not in self.predicate_vocab:
                self.predicate_vocab[predicate] = len(self.predicate_vocab)
                
            for entity in entities:
                if entity not in self.vocab:
                    self.vocab[entity] = len(self.vocab)
                    
            # For now, take first 2 entities for binary relation (can be extended)
            if len(entities) >= 2:
                return {
                    'statement': statement,
                    'predicate': predicate,
                    'entities': entities[:2]  # Use first 2 for compatibility
                }
        return None
        
    def _generate_training_data(self):
        """Generate positive and negative training examples"""
        
        # Positive examples (true facts)
        for fact in self.facts:
            self.labels.append(1.0)  # True fact
            
        # Generate negative examples
        num_negatives = len(self.facts)
        all_predicates = list(self.predicate_vocab.keys())
        all_entities = list(self.vocab.keys())
        
        # Remove special tokens
        all_entities = [e for e in all_entities if not e.startswith('<')]
        all_predicates = [p for p in all_predicates if not p.startswith('<')]
        
        negative_facts = []
        attempts = 0
        max_attempts = num_negatives * 10
        
        while len(negative_facts) < num_negatives and attempts < max_attempts:
            attempts += 1
            
            # Random combination
            pred = np.random.choice(all_predicates)
            ent1 = np.random.choice(all_entities)
            ent2 = np.random.choice(all_entities)
            
            # Create fake fact
            fake_statement = f"{pred}({ent1}, {ent2})."
            
            # Check if it's not a real fact
            if not any(f['statement'] == fake_statement for f in self.facts):
                negative_facts.append({
                    'statement': fake_statement,
                    'predicate': pred,
                    'entities': [ent1, ent2]
                })
                self.labels.append(0.0)  # False fact
                
        # Combine positive and negative
        self.facts.extend(negative_facts)
        
        logger.info(f"Dataset: {sum(self.labels)} positive, {len(self.labels) - sum(self.labels)} negative examples")
        
    def __len__(self):
        return len(self.facts)
        
    def __getitem__(self, idx):
        fact = self.facts[idx]
        label = self.labels[idx]
        
        # Encode entities
        entity_ids = [self.vocab.get(e, 1) for e in fact['entities']]  # 1 is <UNK>
        
        # Encode predicate
        pred_id = self.predicate_vocab.get(fact['predicate'], 0)
        
        return {
            'entities': torch.tensor(entity_ids, dtype=torch.long),
            'predicate': torch.tensor(pred_id, dtype=torch.long),
            'label': torch.tensor(label, dtype=torch.float)
        }


def train_model(model: nn.Module, train_loader: DataLoader, val_loader: DataLoader,
                num_epochs: int = 50, learning_rate: float = 0.001, device: str = 'cuda'):
    """Train the HRM model"""
    
    model = model.to(device)
    criterion = nn.BCELoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    
    best_val_acc = 0
    best_model_state = None
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch in train_loader:
            entities = batch['entities'].to(device)
            predicates = batch['predicate'].to(device)
            labels = batch['label'].to(device)
            
            optimizer.zero_grad()
            outputs = model(entities, predicates)
            loss = criterion(outputs, labels)
            loss.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            train_loss += loss.item()
            predictions = (outputs > 0.5).float()
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)
            
        # Validation
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in val_loader:
                entities = batch['entities'].to(device)
                predicates = batch['predicate'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(entities, predicates)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                predictions = (outputs > 0.5).float()
                val_correct += (predictions == labels).sum().item()
                val_total += labels.size(0)
                
        # Calculate metrics
        train_acc = train_correct / train_total
        val_acc = val_correct / val_total
        avg_train_loss = train_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        
        # Update scheduler
        scheduler.step(avg_val_loss)
        
        # Save best model
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_model_state = model.state_dict().copy()
            
        # Logging
        if (epoch + 1) % 5 == 0:
            logger.info(f"Epoch [{epoch+1}/{num_epochs}]")
            logger.info(f"  Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.4f}")
            logger.info(f"  Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.4f}")
            logger.info(f"  Best Val Acc: {best_val_acc:.4f}")
            
    # Load best model
    if best_model_state:
        model.load_state_dict(best_model_state)
        
    return model, best_val_acc


def save_model(model: nn.Module, vocab: Dict, predicate_vocab: Dict, 
               save_path: str, metrics: Dict[str, float]):
    """Save trained model with metadata"""
    
    checkpoint = {
        'model_state_dict': model.state_dict(),
        'model_config': {
            'vocab_size': len(vocab),
            'embedding_dim': 128,
            'hidden_dim': 256,
            'num_layers': 2,
            'dropout': 0.2
        },
        'vocab': vocab,
        'predicate_vocab': predicate_vocab,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    }
    
    torch.save(checkpoint, save_path)
    logger.info(f"Model saved to {save_path}")


def main():
    """Main training pipeline"""
    
    print("="*60)
    print("HRM NEURAL MODEL TRAINING")
    print("="*60)
    
    # Configuration
    config = {
        'db_path': 'D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db',  # CORRECT DATABASE!
        'model_save_path': 'D:/MCP Mods/HAK_GAL_HEXAGONAL/models/hrm_model_v3_trained.pth',
        'max_facts': 15000,  # Use all 15k facts!
        'batch_size': 64,    # Larger batch for RTX 3080 Ti
        'num_epochs': 100,
        'learning_rate': 0.001,
        'validation_split': 0.2
    }
    
    # Check CUDA
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Using device: {device}")
    if device == 'cuda':
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        
    # Load dataset
    logger.info("Loading dataset...")
    dataset = FactDataset(config['db_path'], config['max_facts'])
    
    if len(dataset) == 0:
        logger.error("No data loaded! Check database path.")
        return
        
    # Split dataset
    val_size = int(len(dataset) * config['validation_split'])
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=config['batch_size'], shuffle=False)
    
    logger.info(f"Training samples: {len(train_dataset)}, Validation samples: {len(val_dataset)}")
    
    # Initialize model
    model = ImprovedHRM(
        vocab_size=len(dataset.vocab),
        embedding_dim=128,
        hidden_dim=256,
        num_layers=2,
        dropout=0.2
    )
    
    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model parameters: {total_params:,}")
    
    # Train model
    logger.info("Starting training...")
    model, best_acc = train_model(
        model, train_loader, val_loader,
        num_epochs=config['num_epochs'],
        learning_rate=config['learning_rate'],
        device=device
    )
    
    # Save model
    Path(config['model_save_path']).parent.mkdir(parents=True, exist_ok=True)
    save_model(
        model, 
        dataset.vocab, 
        dataset.predicate_vocab,
        config['model_save_path'],
        {'best_validation_accuracy': best_acc}
    )
    
    print("\n" + "="*60)
    print("TRAINING COMPLETE!")
    print("="*60)
    print(f"Best Validation Accuracy: {best_acc:.4f}")
    print(f"Model saved to: {config['model_save_path']}")
    print("\nNext steps:")
    print("1. Integrate the trained model into HRM system")
    print("2. Update hrm_system.py to load the new model")
    print("3. Restart the backend to use the trained model")
    

if __name__ == "__main__":
    main()
