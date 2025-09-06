import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import logging
import os
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Matplotlib Styling für Maximum-Impact
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Konfigurierbare Parameter
URL = "http://127.0.0.1:5002/api/facts"  # HAK/GAL API URL
OUTPUT_DIR = "output"

# Logging konfigurieren
logging.basicConfig(filename='scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_data(url):
    """Scrapes data from the HAK/GAL API."""
    try:
        headers = {'X-API-Key': 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        
        # HAK/GAL API gibt JSON zurück
        data = response.json()
        
        # Extrahiere Fakten aus der API-Response
        facts = []
        if 'facts' in data:
            for fact in data['facts']:
                facts.append({
                    'statement': fact.get('statement', ''),
                    'source': fact.get('source', ''),
                    'tags': fact.get('tags', [])
                })
        
        return facts
    except requests.exceptions.RequestException as e:
        logging.error(f"Fehler beim Abrufen der URL: {e}")
        return None
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
        return None

def analyze_data(facts):
    """Analysiert die gesammelten Daten."""
    df = pd.DataFrame(facts)
    
    # Häufigkeitsanalyse der Statements
    statement_counts = df['statement'].value_counts()
    
    # Analyse der Tags
    all_tags = []
    for tags in df['tags']:
        if isinstance(tags, list):
            all_tags.extend(tags)
        elif isinstance(tags, str):
            all_tags.extend(tags.split(','))
    
    tag_counts = pd.Series(all_tags).value_counts()
    
    return df, statement_counts, tag_counts

def visualize_data(df, statement_counts, tag_counts):
    """MAXIMUM POWER Visualisierung - Alle Charts, alle Formate!"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("🚀 MAXIMUM VISUALIZATION POWER ACTIVATED!")
    
    # 1. MATPLOTLIB CHARTS - Maximum Styling
    if len(statement_counts) > 0:
        # Statement Bar Chart - Enhanced
        fig, ax = plt.subplots(figsize=(16, 10))
        top_statements = statement_counts.head(15)
        bars = ax.bar(range(len(top_statements)), top_statements.values, 
                     color=plt.cm.viridis(np.linspace(0, 1, len(top_statements))))
        ax.set_title('🔥 TOP 15 HAK/GAL STATEMENTS - MAXIMUM IMPACT', fontsize=16, fontweight='bold')
        ax.set_xlabel('Statements', fontsize=12, fontweight='bold')
        ax.set_ylabel('Häufigkeit', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(top_statements)))
        ax.set_xticklabels([s[:50] + '...' if len(s) > 50 else s for s in top_statements.index], 
                          rotation=45, ha='right')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{int(height)}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'statement_counts_enhanced.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 ENHANCED Statement-Diagramm erstellt (300 DPI)")
        
        # Statement Pie Chart
        plt.figure(figsize=(14, 10))
        top_10 = statement_counts.head(10)
        colors = plt.cm.Set3(np.linspace(0, 1, len(top_10)))
        wedges, texts, autotexts = plt.pie(top_10.values, labels=top_10.index, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        plt.title('🎯 TOP 10 STATEMENTS - PIE CHART POWER', fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'statement_pie_chart.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("🥧 Statement-Pie-Chart erstellt")
    
    # 2. SEABORN HEATMAP - Advanced Analytics
    if len(df) > 0:
        plt.figure(figsize=(16, 10))
        # Create correlation matrix for numerical data
        df_numeric = df.select_dtypes(include=[np.number])
        if len(df_numeric.columns) > 1:
            correlation_matrix = df_numeric.corr()
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5, cbar_kws={"shrink": .8})
            plt.title('🔥 HAK/GAL DATA CORRELATION HEATMAP', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
            plt.close()
            print("🔥 Correlation Heatmap erstellt")
    
    # 3. PLOTLY INTERACTIVE CHARTS - Maximum Interactivity
    if len(statement_counts) > 0:
        # Interactive Bar Chart
        fig = go.Figure(data=[
            go.Bar(x=list(statement_counts.head(20).index),
                   y=list(statement_counts.head(20).values),
                   marker_color=px.colors.qualitative.Set3,
                   text=list(statement_counts.head(20).values),
                   textposition='auto',
                   hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>')
        ])
        
        fig.update_layout(
            title=dict(text='🚀 HAK/GAL STATEMENTS - INTERACTIVE POWER', 
                      font=dict(size=20, color='darkblue')),
            xaxis_title="Statements",
            yaxis_title="Count",
            font=dict(size=12),
            height=600,
            showlegend=False
        )
        
        fig.write_html(os.path.join(OUTPUT_DIR, 'interactive_statements.html'))
        print("🌐 Interactive HTML Chart erstellt")
        
        # 3D Scatter Plot (if we have enough data)
        if len(df) > 10:
            fig_3d = go.Figure(data=[go.Scatter3d(
                x=list(range(len(df))),
                y=[len(str(x)) for x in df['statement']],
                z=[len(str(x).split()) for x in df['statement']],
                mode='markers',
                marker=dict(
                    size=8,
                    color=list(range(len(df))),
                    colorscale='Viridis',
                    opacity=0.8
                ),
                text=df['statement'].str[:50] + '...',
                hovertemplate='<b>%{text}</b><br>Length: %{y}<br>Words: %{z}<extra></extra>'
            )])
            
            fig_3d.update_layout(
                title='🎯 HAK/GAL DATA - 3D ANALYSIS',
                scene=dict(
                    xaxis_title='Index',
                    yaxis_title='Statement Length',
                    zaxis_title='Word Count'
                ),
                height=600
            )
            
            fig_3d.write_html(os.path.join(OUTPUT_DIR, '3d_analysis.html'))
            print("🎯 3D Analysis Chart erstellt")
    
    # 4. ADVANCED STATISTICS VISUALIZATION
    if len(statement_counts) > 0:
        # Box Plot for statement lengths
        statement_lengths = [len(str(x)) for x in statement_counts.index]
        plt.figure(figsize=(12, 8))
        plt.boxplot(statement_lengths, patch_artist=True,
                   boxprops=dict(facecolor='lightblue', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2))
        plt.title('📊 STATEMENT LENGTH DISTRIBUTION', fontsize=16, fontweight='bold')
        plt.ylabel('Character Count', fontsize=12, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'statement_length_boxplot.png'), dpi=300, bbox_inches='tight')
        plt.close()
        print("📊 Statement Length Boxplot erstellt")
    
    print("🚀 MAXIMUM VISUALIZATION COMPLETE - ALL CHARTS GENERATED!")

def export_results(df, filename):
    """Exportiert die Daten in JSON und CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_json(os.path.join(OUTPUT_DIR, f"{filename}.json"), orient='records')
    df.to_csv(os.path.join(OUTPUT_DIR, f"{filename}.csv"), index=False)

def generate_html_report(df, statement_counts, tag_counts):
    """MAXIMUM POWER HTML-Report mit allen Visualisierungen!"""
    
    # Generate comprehensive statistics
    total_facts = len(df)
    unique_statements = len(statement_counts)
    unique_tags = len(tag_counts)
    avg_statement_length = np.mean([len(str(x)) for x in df['statement']]) if len(df) > 0 else 0
    max_statement_length = np.max([len(str(x)) for x in df['statement']]) if len(df) > 0 else 0
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 HAK/GAL MAXIMUM POWER ANALYSIS REPORT</title>
        <meta charset="UTF-8">
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
            }}
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                border-radius: 15px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{ 
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4); 
                color: white; 
                padding: 30px; 
                text-align: center; 
            }}
            .header h1 {{ 
                margin: 0; 
                font-size: 2.5em; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                padding: 30px; 
                background: #f8f9fa;
            }}
            .stat-card {{ 
                background: white; 
                padding: 20px; 
                border-radius: 10px; 
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 5px solid #4ecdc4;
            }}
            .stat-number {{ 
                font-size: 2em; 
                font-weight: bold; 
                color: #4ecdc4; 
                margin-bottom: 10px;
            }}
            .content {{ padding: 30px; }}
            h2 {{ 
                color: #2c3e50; 
                border-bottom: 3px solid #4ecdc4; 
                padding-bottom: 10px;
                margin-top: 30px;
            }}
            table {{ 
                border-collapse: collapse; 
                width: 100%; 
                margin: 20px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            th, td {{ 
                border: none; 
                padding: 15px; 
                text-align: left; 
            }}
            th {{ 
                background: linear-gradient(45deg, #4ecdc4, #44a08d); 
                color: white; 
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            tr:nth-child(even) {{ background-color: #f8f9fa; }}
            tr:hover {{ background-color: #e3f2fd; transform: scale(1.01); transition: all 0.3s ease; }}
            .chart-container {{ 
                margin: 30px 0; 
                text-align: center;
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
            }}
            .chart-container img {{ 
                max-width: 100%; 
                height: auto; 
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }}
            .footer {{ 
                background: #2c3e50; 
                color: white; 
                text-align: center; 
                padding: 20px; 
            }}
            .emoji {{ font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 HAK/GAL MAXIMUM POWER ANALYSIS</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{total_facts:,}</div>
                    <div>Total Facts</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{unique_statements:,}</div>
                    <div>Unique Statements</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{unique_tags:,}</div>
                    <div>Unique Tags</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{avg_statement_length:.1f}</div>
                    <div>Avg Statement Length</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{max_statement_length:,}</div>
                    <div>Max Statement Length</div>
                </div>
            </div>
            
            <div class="content">
                <h2>📊 Visualizations</h2>
                <div class="chart-container">
                    <h3>🔥 Enhanced Statement Analysis</h3>
                    <img src="statement_counts_enhanced.png" alt="Enhanced Statement Chart">
                </div>
                
                <div class="chart-container">
                    <h3>🥧 Statement Distribution</h3>
                    <img src="statement_pie_chart.png" alt="Statement Pie Chart">
                </div>
                
                <div class="chart-container">
                    <h3>📊 Statement Length Distribution</h3>
                    <img src="statement_length_boxplot.png" alt="Statement Length Boxplot">
                </div>
                
                <h2>🏆 Top 15 Statements</h2>
                <table>
                    <tr><th>Rank</th><th>Statement</th><th>Count</th><th>Percentage</th></tr>
    """
    
    if len(statement_counts) > 0:
        total_count = statement_counts.sum()
        for i, (statement, count) in enumerate(statement_counts.head(15).items(), 1):
            percentage = (count / total_count) * 100
            html_content += f"""
            <tr>
                <td><span class="emoji">#{i}</span></td>
                <td>{statement[:100]}{'...' if len(statement) > 100 else ''}</td>
                <td><strong>{count:,}</strong></td>
                <td>{percentage:.2f}%</td>
            </tr>"""
    else:
        html_content += "<tr><td colspan='4'>Keine Statements verfügbar</td></tr>"
    
    html_content += """
                </table>
                
                <h2>🌐 Interactive Charts</h2>
                <div class="chart-container">
                    <h3>🚀 Interactive Statement Analysis</h3>
                    <p><a href="interactive_statements.html" target="_blank" style="color: #4ecdc4; text-decoration: none; font-weight: bold;">📈 Open Interactive Chart →</a></p>
                </div>
                
                <div class="chart-container">
                    <h3>🎯 3D Data Analysis</h3>
                    <p><a href="3d_analysis.html" target="_blank" style="color: #4ecdc4; text-decoration: none; font-weight: bold;">🎯 Open 3D Analysis →</a></p>
                </div>
                
                <h2>📈 Data Export Files</h2>
                <table>
                    <tr><th>File Type</th><th>Description</th><th>Size</th></tr>
                    <tr><td>📊 CSV</td><td>Structured data export</td><td>hak_gal_data.csv</td></tr>
                    <tr><td>📋 JSON</td><td>Machine-readable format</td><td>hak_gal_data.json</td></tr>
                    <tr><td>🌐 HTML</td><td>Interactive charts</td><td>interactive_statements.html</td></tr>
                    <tr><td>🎯 3D</td><td>3D analysis</td><td>3d_analysis.html</td></tr>
                </table>
            </div>
            
            <div class="footer">
                <p>🚀 Generated by HAK/GAL Multi-Agent System | Maximum Power Analysis</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(os.path.join(OUTPUT_DIR, 'report.html'), 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("🚀 MAXIMUM POWER HTML-Report erstellt!")

if __name__ == "__main__":
    logging.info("HAK/GAL Webscraper gestartet...")
    facts = scrape_data(URL)
    if facts:
        logging.info(f"{len(facts)} Fakten extrahiert.")
        df, statement_counts, tag_counts = analyze_data(facts)
        visualize_data(df, statement_counts, tag_counts)
        export_results(df, "hak_gal_data")
        generate_html_report(df, statement_counts, tag_counts)
        logging.info("Ergebnisse exportiert.")
        print(f"✅ {len(facts)} Fakten erfolgreich verarbeitet!")
        print(f"📊 {len(statement_counts)} eindeutige Statements gefunden")
        print(f"🏷️ {len(tag_counts)} eindeutige Tags gefunden")
        print(f"📁 Ergebnisse gespeichert in: {OUTPUT_DIR}/")
    else:
        logging.error("Scraping fehlgeschlagen.")
        print("❌ Scraping fehlgeschlagen!")
