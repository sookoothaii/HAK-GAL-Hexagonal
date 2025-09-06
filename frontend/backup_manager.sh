#!/bin/bash
# HAK_GAL Frontend Backup Manager (Linux/Mac Version)

timestamp=$(date +"%Y%m%d_%H%M%S")
backup_dir="D:/MCP Mods/HAK_GAL_HEXAGONAL/frontend_backups/backup_$timestamp"
source_dir="D:/MCP Mods/HAK_GAL_HEXAGONAL/frontend"
rollback_log="D:/MCP Mods/HAK_GAL_HEXAGONAL/frontend_backups/rollback.log"

create_backup() {
    echo "🔒 Creating Frontend Backup..."
    
    # Create backup directory
    mkdir -p "$backup_dir"
    
    # Copy all frontend files
    echo "📁 Backing up src directory..."
    cp -r "$source_dir/src" "$backup_dir/"
    
    echo "📄 Backing up configuration files..."
    cp "$source_dir/package.json" "$backup_dir/"
    cp "$source_dir/package-lock.json" "$backup_dir/" 2>/dev/null || true
    cp "$source_dir/.env" "$backup_dir/"
    cp "$source_dir/vite.config.ts" "$backup_dir/"
    cp "$source_dir/tsconfig.json" "$backup_dir/"
    
    # Create backup metadata
    cat > "$backup_dir/backup_metadata.json" << EOF
{
    "timestamp": "$timestamp",
    "date": "$(date +'%Y-%m-%d %H:%M:%S')",
    "files": $(find "$source_dir" -type f | wc -l),
    "node_version": "$(node --version)",
    "npm_version": "$(npm --version)"
}
EOF
    
    # Log backup
    echo "[$timestamp] Backup created: $backup_dir" >> "$rollback_log"
    
    echo "✅ Backup completed: $backup_dir"
    echo "📊 Total files backed up: $(find "$source_dir" -type f | wc -l)"
}

# Create initial backup
if [ "$1" == "backup" ]; then
    create_backup
else
    echo "Usage: ./backup_manager.sh backup"
fi
