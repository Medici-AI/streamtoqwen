#!/usr/bin/env python3
"""
Export System Architecture to PDF
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np
from datetime import datetime

def create_architecture_pdf():
    """Create a PDF of the system architecture diagram."""
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(16, 20))
    fig.suptitle('🎤 ElevenLabs Multi-Agent Conversational AI System Architecture', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fig.text(0.5, 0.96, f'Generated: {timestamp}', ha='center', fontsize=10, style='italic')
    
    # 1. Data Flow Diagram
    ax1 = plt.subplot(4, 1, 1)
    ax1.set_title('📊 Data Flow Architecture', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 8)
    ax1.axis('off')
    
    # Data flow components
    components = [
        ('🎤 Microphone Input', 5, 7, 'lightblue'),
        ('🔗 ElevenLabs WebSocket', 5, 6, 'lightgreen'),
        ('📝 Conversation Context Builder', 5, 5, 'lightyellow'),
        ('🔄 LangGraph Flow Orchestrator', 5, 4, 'lightcoral'),
        ('🤖 Multi-Agent Parallel Execution', 5, 3, 'lightpink'),
        ('🧠 Mem0 Consolidation Engine', 5, 2, 'lightsteelblue'),
        ('📊 Strategic Output & Recommendations', 5, 1, 'lightgoldenrodyellow')
    ]
    
    for name, x, y, color in components:
        box = FancyBboxPatch((x-1.5, y-0.3), 3, 0.6, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, edgecolor='black', linewidth=1)
        ax1.add_patch(box)
        ax1.text(x, y, name, ha='center', va='center', fontsize=10, fontweight='bold')
    
    # Add arrows
    for i in range(len(components)-1):
        y1 = components[i][2] - 0.3
        y2 = components[i+1][2] + 0.3
        arrow = ConnectionPatch((5, y1), (5, y2), "data", "data",
                              arrowstyle="->", shrinkA=5, shrinkB=5, 
                              mutation_scale=20, fc="red", linewidth=2)
        ax1.add_patch(arrow)
    
    # 2. Agent Architecture
    ax2 = plt.subplot(4, 1, 2)
    ax2.set_title('🤖 Agent Architecture', fontsize=14, fontweight='bold', pad=20)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 6)
    ax2.axis('off')
    
    # Agent boxes
    agents = [
        ('🔵 Intent Agent\n(Quen LLM)', 2, 5, 'lightblue'),
        ('🟡 Strategy Agent\n(GPT-4o)', 8, 5, 'lightyellow'),
        ('🟢 Sentiment Agent\n(Quen LLM)', 2, 3, 'lightgreen'),
        ('🟣 Learning Agent\n(GPT-4o)', 8, 3, 'plum'),
        ('🔴 Decision Agent\n(Quen LLM)', 5, 1, 'lightcoral')
    ]
    
    for name, x, y, color in agents:
        box = FancyBboxPatch((x-1.2, y-0.4), 2.4, 0.8, 
                            boxstyle="round,pad=0.1", 
                            facecolor=color, edgecolor='black', linewidth=1)
        ax2.add_patch(box)
        ax2.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # 3. Memory Structure
    ax3 = plt.subplot(4, 1, 3)
    ax3.set_title('🧠 Memory Architecture (Mem0)', fontsize=14, fontweight='bold', pad=20)
    ax3.set_xlim(0, 10)
    ax3.set_ylim(0, 8)
    ax3.axis('off')
    
    # Memory structure
    memory_components = [
        ('data/', 5, 7, 'lightgray'),
        ('intent_agent/', 2, 6, 'lightblue'),
        ('strategy_agent/', 4, 6, 'lightyellow'),
        ('sentiment_agent/', 6, 6, 'lightgreen'),
        ('learning_agent/', 8, 6, 'plum'),
        ('decision_agent/', 3, 5, 'lightcoral'),
        ('mem0_consolidation/', 7, 5, 'lightsteelblue'),
        ('agent_data.json', 1, 4, 'white'),
        ('analysis_log.jsonl', 3, 4, 'white'),
        ('consolidation_*.json', 7, 4, 'white')
    ]
    
    for name, x, y, color in memory_components:
        box = FancyBboxPatch((x-0.8, y-0.2), 1.6, 0.4, 
                            boxstyle="round,pad=0.05", 
                            facecolor=color, edgecolor='black', linewidth=0.5)
        ax3.add_patch(box)
        ax3.text(x, y, name, ha='center', va='center', fontsize=8)
    
    # 4. Performance Characteristics
    ax4 = plt.subplot(4, 1, 4)
    ax4.set_title('⚡ Performance Characteristics', fontsize=14, fontweight='bold', pad=20)
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 6)
    ax4.axis('off')
    
    # Performance metrics
    metrics = [
        ('⏱️ Timing', 2, 5, 'lightblue'),
        ('🎯 Accuracy', 5, 5, 'lightgreen'),
        ('🔄 Scalability', 8, 5, 'lightcoral'),
        ('Window Size: 3s/5s/10s', 2, 4, 'white'),
        ('Agent Timeout: 30s', 2, 3.5, 'white'),
        ('Parallel Execution', 5, 4, 'white'),
        ('Independent Storage', 8, 4, 'white'),
        ('Configurable Windows', 8, 3.5, 'white')
    ]
    
    for name, x, y, color in metrics:
        box = FancyBboxPatch((x-1.5, y-0.2), 3, 0.4, 
                            boxstyle="round,pad=0.05", 
                            facecolor=color, edgecolor='black', linewidth=0.5)
        ax4.add_patch(box)
        ax4.text(x, y, name, ha='center', va='center', fontsize=9)
    
    # Add system components table
    fig.text(0.02, 0.02, '''
📋 System Components:
• Intent Agent (Quen LLM) - Customer intent analysis
• Strategy Agent (GPT-4o) - Strategic recommendations  
• Sentiment Agent (Quen LLM) - Emotional state analysis
• Learning Agent (GPT-4o) - Pattern recognition
• Decision Agent (Quen LLM) - Action planning
• Mem0 Consolidator - Cross-agent insights
• LangGraph Flow - Parallel execution orchestration
• ElevenLabs Client - Real-time WebSocket communication
• Microphone Client - Audio capture and processing
    ''', fontsize=10, style='italic')
    
    plt.tight_layout()
    
    # Save as PDF
    filename = f"system_architecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    plt.savefig(filename, format='pdf', dpi=300, bbox_inches='tight')
    print(f"✅ Architecture diagram saved as: {filename}")
    
    return filename

def create_simple_text_pdf():
    """Create a simple text-based PDF using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        
        # Create PDF document
        filename = f"system_architecture_text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("🎤 ElevenLabs Multi-Agent Conversational AI System Architecture", title_style))
        story.append(Spacer(1, 20))
        
        # Data Flow Section
        story.append(Paragraph("📊 Data Flow Architecture", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        flow_data = [
            ['🎤 Microphone Input', 'Real-time audio capture via PyAudio'],
            ['🔗 ElevenLabs WebSocket', 'WebSocket communication with ElevenLabs API'],
            ['📝 Conversation Context Builder', 'Cumulative context building from messages'],
            ['🔄 LangGraph Flow Orchestrator', 'Parallel agent execution coordination'],
            ['🤖 Multi-Agent Parallel Execution', '5 specialized agents analyzing simultaneously'],
            ['🧠 Mem0 Consolidation Engine', 'Cross-agent insight extraction and consolidation'],
            ['📊 Strategic Output & Recommendations', 'Final strategic recommendations and analysis']
        ]
        
        flow_table = Table(flow_data, colWidths=[2*inch, 4*inch])
        flow_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(flow_table)
        story.append(Spacer(1, 20))
        
        # Agent Architecture Section
        story.append(Paragraph("🤖 Agent Architecture", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        agent_data = [
            ['Agent', 'LLM', 'Specialization', 'Key Functions'],
            ['🔵 Intent Agent', 'Quen LLM', 'Customer Intent Analysis', 'Primary intent, motivations, confidence'],
            ['🟡 Strategy Agent', 'GPT-4o', 'Strategic Recommendations', 'Strategic approach, opportunities, risks'],
            ['🟢 Sentiment Agent', 'Quen LLM', 'Emotional Analysis', 'Emotional state, sentiment, trust level'],
            ['🟣 Learning Agent', 'GPT-4o', 'Pattern Recognition', 'Patterns, knowledge, behavioral trends'],
            ['🔴 Decision Agent', 'Quen LLM', 'Action Planning', 'Immediate actions, priorities, alternatives']
        ]
        
        agent_table = Table(agent_data, colWidths=[1.2*inch, 1.2*inch, 1.8*inch, 2.8*inch])
        agent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.royalblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(agent_table)
        story.append(Spacer(1, 20))
        
        # Memory Structure Section
        story.append(Paragraph("🧠 Memory Architecture (Mem0)", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        memory_text = """
        📁 File System Storage Structure:
        
        data/
        ├── intent_agent/
        │   ├── agent_data.json
        │   ├── analysis_log.jsonl
        │   └── customer_profiles.json
        ├── strategy_agent/
        │   ├── agent_data.json
        │   ├── analysis_log.jsonl
        │   └── strategies.json
        ├── sentiment_agent/
        │   ├── agent_data.json
        │   ├── analysis_log.jsonl
        │   └── emotion_tracker.json
        ├── learning_agent/
        │   ├── agent_data.json
        │   ├── analysis_log.jsonl
        │   └── learned_patterns.json
        ├── decision_agent/
        │   ├── agent_data.json
        │   ├── analysis_log.jsonl
        │   └── decisions.json
        └── mem0_consolidation/
            └── consolidation_YYYYMMDD_HHMMSS.json
        """
        
        story.append(Paragraph(memory_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Performance Characteristics Section
        story.append(Paragraph("⚡ Performance Characteristics", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        perf_data = [
            ['Metric', 'Value', 'Description'],
            ['Window Size', '3s/5s/10s', 'Configurable analysis windows'],
            ['Agent Timeout', '30s', 'Per-agent analysis timeout'],
            ['Total Analysis', '120s', 'Complete multi-agent analysis timeout'],
            ['Parallel Execution', 'Yes', 'All agents run simultaneously'],
            ['Independent Storage', 'Yes', 'Each agent has separate memory store'],
            ['Colored Output', 'Yes', 'Distinct colors for each agent']
        ]
        
        perf_table = Table(perf_data, colWidths=[2*inch, 1.5*inch, 3.5*inch])
        perf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(perf_table)
        
        # Build PDF
        doc.build(story)
        print(f"✅ Text-based architecture document saved as: {filename}")
        return filename
        
    except ImportError:
        print("❌ reportlab not available. Install with: pip install reportlab")
        return None

def main():
    """Main function to create PDF exports."""
    print("🔄 Creating PDF exports of system architecture...")
    
    # Try matplotlib version first
    try:
        filename1 = create_architecture_pdf()
        print(f"✅ Visual diagram: {filename1}")
    except Exception as e:
        print(f"❌ Error creating visual diagram: {e}")
        filename1 = None
    
    # Try reportlab version
    filename2 = create_simple_text_pdf()
    
    if filename1 or filename2:
        print("\n🎉 PDF export completed!")
        if filename1:
            print(f"📊 Visual diagram: {filename1}")
        if filename2:
            print(f"📄 Text document: {filename2}")
    else:
        print("❌ Failed to create PDF exports")

if __name__ == "__main__":
    main() 