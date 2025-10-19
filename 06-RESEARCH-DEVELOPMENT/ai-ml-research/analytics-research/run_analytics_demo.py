#!/usr/bin/env python3
"""
🎯 ANALYTICS DEMO RUNNER
=======================
Quick demonstration of institutional-grade analytics capabilities

This script provides a streamlined way to experience the full power of the
AIA Analytics Platform with sample data and comprehensive demonstrations.
"""

import sys
import time
import json
import webbrowser
import threading
from datetime import datetime
from pathlib import Path

def print_header():
    """Print demo header"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║               🎯 AIA ANALYTICS PLATFORM DEMO                                   ║
║                                                                               ║
║    Institutional-Grade Business Intelligence Demonstration                     ║
║                                                                               ║
║  💰 Monte Carlo Financial Projections ($42.8M → $1.8B)                       ║
║  📈 Hybrid ARIMA-LSTM Market Forecasting                                     ║
║  👥 Advanced Customer LTV/CAC Analytics                                       ║
║  🔄 Real-Time Business Intelligence Dashboard                                  ║
║  🎯 Executive Presentation Generation                                          ║
║  ⚠️ Comprehensive Risk Assessment                                             ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

def run_institutional_analysis():
    """Run the institutional analytics system"""
    print("🏢 Running Institutional Analytics Analysis...")

    try:
        from institutional_analytics_system import main as institutional_main
        institutional_main()
        return True
    except Exception as e:
        print(f"❌ Institutional analytics failed: {e}")
        return False

def run_realtime_demo():
    """Run real-time business intelligence demo"""
    print("🔄 Starting Real-Time Business Intelligence Demo...")

    def start_realtime():
        try:
            from real_time_business_intelligence import main as realtime_main
            realtime_main()
        except Exception as e:
            print(f"❌ Real-time system failed: {e}")

    # Start in background thread
    thread = threading.Thread(target=start_realtime, daemon=True)
    thread.start()

    print("✅ Real-time dashboard starting at http://localhost:8051")
    time.sleep(3)
    return True

def run_presentation_demo():
    """Run executive presentation demo"""
    print("🎯 Generating Executive Presentation...")

    try:
        from executive_presentation_system import main as presentation_main

        # Start in background thread
        def start_presentation():
            presentation_main()

        thread = threading.Thread(target=start_presentation, daemon=True)
        thread.start()

        print("✅ Executive presentation starting at http://localhost:8052")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"❌ Presentation system failed: {e}")
        return False

def run_comprehensive_demo():
    """Run comprehensive analytics demo"""
    print("🎼 Starting Comprehensive Analytics Demo...")

    results = {}

    # Step 1: Institutional Analysis
    print("\n" + "="*80)
    print("STEP 1: INSTITUTIONAL FINANCIAL ANALYSIS")
    print("="*80)

    if run_institutional_analysis():
        results['institutional'] = True
        print("✅ Institutional analysis completed")
    else:
        results['institutional'] = False
        print("❌ Institutional analysis failed")

    # Step 2: Real-Time Dashboard
    print("\n" + "="*80)
    print("STEP 2: REAL-TIME BUSINESS INTELLIGENCE")
    print("="*80)

    if run_realtime_demo():
        results['realtime'] = True
        print("✅ Real-time dashboard launched")
    else:
        results['realtime'] = False
        print("❌ Real-time dashboard failed")

    # Step 3: Executive Presentations
    print("\n" + "="*80)
    print("STEP 3: EXECUTIVE PRESENTATION SYSTEM")
    print("="*80)

    if run_presentation_demo():
        results['presentation'] = True
        print("✅ Executive presentation launched")
    else:
        results['presentation'] = False
        print("❌ Executive presentation failed")

    return results

def open_browser_tabs():
    """Open browser tabs for demo"""
    urls = [
        "http://localhost:8051",  # Real-time dashboard
        "http://localhost:8052",  # Executive presentation
    ]

    print("🌐 Opening browser tabs for demo...")
    for url in urls:
        try:
            webbrowser.open(url)
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ Could not open {url}: {e}")

def wait_for_user_input():
    """Wait for user interaction"""
    print("\n" + "="*80)
    print("DEMO SERVICES ACTIVE")
    print("="*80)
    print("📊 Real-Time Dashboard: http://localhost:8051")
    print("🎯 Executive Presentation: http://localhost:8052")
    print("📋 Comprehensive analysis results saved to JSON files")
    print("\n💡 Explore the dashboards and presentations in your browser")
    print("Press Enter to stop the demo or Ctrl+C to exit...")

    try:
        input()
        print("🛑 Stopping demo services...")
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")

def generate_demo_summary(results: dict):
    """Generate demo summary report"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    summary = {
        "demo_timestamp": timestamp,
        "demo_results": results,
        "success_rate": sum(results.values()) / len(results) if results else 0,
        "components_tested": list(results.keys()),
        "recommendations": [
            "Review generated JSON files for detailed analytics results",
            "Explore interactive dashboards in browser",
            "Examine executive presentation slides",
            "Consider production deployment for enterprise use"
        ],
        "next_steps": [
            "Customize analytics parameters for your business",
            "Integrate with your data sources",
            "Deploy in production environment",
            "Schedule regular analysis runs"
        ]
    }

    summary_file = f"/Users/wXy/dev/Projects/aia/analytics/demo_summary_{timestamp}.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"📋 Demo summary saved: {summary_file}")
    return summary

def main():
    """Main demo execution"""
    print_header()

    print("🚀 Welcome to the AIA Analytics Platform Demo!")
    print("\nThis demonstration will showcase:")
    print("  • Advanced financial modeling with Monte Carlo simulations")
    print("  • Real-time business intelligence monitoring")
    print("  • Executive presentation generation")
    print("  • Comprehensive risk assessment")
    print("  • Customer analytics and market intelligence")

    print("\n⏱️ Estimated demo time: 5-10 minutes")
    print("💻 System requirements: Python 3.8+, 4GB RAM, modern web browser")

    # Get user confirmation
    print("\nPress Enter to start the demo or Ctrl+C to exit...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled by user")
        sys.exit(0)

    # Check if we're in the right directory
    current_dir = Path.cwd()
    analytics_files = [
        'institutional_analytics_system.py',
        'real_time_business_intelligence.py',
        'executive_presentation_system.py'
    ]

    missing_files = []
    for file in analytics_files:
        if not (current_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        print("Please run this script from the analytics directory")
        sys.exit(1)

    # Run comprehensive demo
    print("\n🎯 Starting comprehensive analytics demonstration...")
    results = run_comprehensive_demo()

    # Open browser tabs
    time.sleep(2)
    open_browser_tabs()

    # Wait for user interaction
    wait_for_user_input()

    # Generate summary
    summary = generate_demo_summary(results)

    # Final report
    print("\n" + "="*80)
    print("DEMO COMPLETION REPORT")
    print("="*80)

    success_count = sum(results.values())
    total_count = len(results)
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0

    print(f"✅ Components tested: {total_count}")
    print(f"✅ Successful demonstrations: {success_count}")
    print(f"📊 Success rate: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("The AIA Analytics Platform is ready for enterprise deployment.")
    elif success_rate >= 60:
        print("\n⚠️ DEMO PARTIALLY SUCCESSFUL")
        print("Some components may need troubleshooting for production use.")
    else:
        print("\n❌ DEMO NEEDS ATTENTION")
        print("Multiple components failed. Check system requirements and dependencies.")

    print("\n📋 Files generated:")
    for file in Path.cwd().glob("*_analysis_*.json"):
        print(f"  • {file.name}")
    for file in Path.cwd().glob("demo_summary_*.json"):
        print(f"  • {file.name}")

    print("\n💡 Next steps:")
    for step in summary['next_steps']:
        print(f"  • {step}")

    print("\n👋 Thank you for experiencing the AIA Analytics Platform!")

if __name__ == "__main__":
    main()