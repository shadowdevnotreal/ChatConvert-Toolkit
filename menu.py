#!/usr/bin/env python3
"""
ChatConvert Toolkit - Universal Cross-Platform Menu
Converts chat files from 10+ input formats to 8 output formats.

Compatible with: Windows, macOS, Linux
Python 3.6+
"""

import os
import sys
import platform
import subprocess
import importlib.util
from pathlib import Path

# Add chatconvert to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from chatconvert import ConversionEngine
    from chatconvert.analytics import AnalyticsEngine
except ImportError:
    ConversionEngine = None
    AnalyticsEngine = None


# Color codes for different platforms
class Colors:
    """ANSI color codes with Windows compatibility."""

    def __init__(self):
        self.enabled = self._check_color_support()

        if self.enabled:
            self.RED = '\033[0;31m'
            self.GREEN = '\033[0;32m'
            self.YELLOW = '\033[1;33m'
            self.BLUE = '\033[0;34m'
            self.PURPLE = '\033[0;35m'
            self.CYAN = '\033[0;36m'
            self.BOLD = '\033[1m'
            self.NC = '\033[0m'  # No Color
        else:
            # No colors for unsupported terminals
            self.RED = self.GREEN = self.YELLOW = self.BLUE = ''
            self.PURPLE = self.CYAN = self.BOLD = self.NC = ''

    def _check_color_support(self):
        """Check if terminal supports colors."""
        # Enable colors on Windows 10+
        if platform.system() == 'Windows':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False

        # Enable colors on Unix-like systems
        return sys.stdout.isatty()


# Global color instance
colors = Colors()


def clear_screen():
    """Clear terminal screen (cross-platform)."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def print_header():
    """Print colorful header."""
    clear_screen()
    print(f"{colors.PURPLE}╔════════════════════════════════════════════════════════╗{colors.NC}")
    print(f"{colors.PURPLE}║{colors.NC}  {colors.BOLD}{colors.CYAN}💬 ChatConvert Toolkit{colors.NC}                         {colors.PURPLE}║{colors.NC}")
    print(f"{colors.PURPLE}║{colors.NC}  {colors.YELLOW}Universal chat format converter & analyzer{colors.NC}       {colors.PURPLE}║{colors.NC}")
    print(f"{colors.PURPLE}╚════════════════════════════════════════════════════════╝{colors.NC}")
    print()


def get_python_command():
    """Detect the correct Python command (python3 or python)."""
    # Try python3 first
    try:
        result = subprocess.run(['python3', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return 'python3'
    except FileNotFoundError:
        pass

    # Try python
    try:
        result = subprocess.run(['python', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            version_str = result.stdout + result.stderr
            # Check if it's Python 3
            if 'Python 3' in version_str:
                return 'python'
    except FileNotFoundError:
        pass

    return None


def check_python_version():
    """Check if Python version is adequate (3.6+)."""
    if sys.version_info < (3, 6):
        print(f"{colors.RED}✗ Error: Python 3.6 or higher is required!{colors.NC}")
        print(f"{colors.YELLOW}You have: Python {sys.version_info.major}.{sys.version_info.minor}{colors.NC}")
        print(f"{colors.YELLOW}Please upgrade Python and try again.{colors.NC}")
        return False

    print(f"{colors.GREEN}✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected{colors.NC}")
    print(f"{colors.GREEN}✓ Platform: {platform.system()} {platform.release()}{colors.NC}")
    return True


def check_module_installed(module_name):
    """Check if a Python module is installed."""
    return importlib.util.find_spec(module_name) is not None


def install_dependencies():
    """Auto-install required dependencies."""
    print_header()
    print(f"{colors.CYAN}{colors.BOLD}Checking Dependencies...{colors.NC}")
    print()

    # Check for reportlab (only required dependency for PDF)
    if check_module_installed('reportlab'):
        print(f"{colors.GREEN}✓ reportlab is already installed{colors.NC}")
        print()
        input("Press Enter to continue...")
        return True

    print(f"{colors.YELLOW}reportlab not found - required for PDF conversion{colors.NC}")
    print()

    response = input("Install reportlab now? [Y/n]: ").strip().lower()

    if response in ['', 'y', 'yes']:
        print()
        print(f"{colors.YELLOW}Installing reportlab...{colors.NC}")

        python_cmd = get_python_command()
        if not python_cmd:
            print(f"{colors.RED}✗ Could not find Python command{colors.NC}")
            return False

        try:
            # Try installing with pip
            result = subprocess.run(
                [python_cmd, '-m', 'pip', 'install', 'reportlab'],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"{colors.GREEN}✓ reportlab installed successfully!{colors.NC}")
                print()
                input("Press Enter to continue...")
                return True
            else:
                print(f"{colors.RED}✗ Installation failed{colors.NC}")
                print(result.stderr)

                # Try with --user flag
                print(f"{colors.YELLOW}Trying with --user flag...{colors.NC}")
                result = subprocess.run(
                    [python_cmd, '-m', 'pip', 'install', '--user', 'reportlab'],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print(f"{colors.GREEN}✓ reportlab installed successfully!{colors.NC}")
                    print()
                    input("Press Enter to continue...")
                    return True
                else:
                    print(f"{colors.RED}✗ Installation failed{colors.NC}")
                    print(result.stderr)

        except Exception as e:
            print(f"{colors.RED}✗ Error during installation: {e}{colors.NC}")

        print()
        input("Press Enter to continue...")
        return False

    print(f"{colors.YELLOW}Skipping installation. PDF conversion will not be available.{colors.NC}")
    print()
    input("Press Enter to continue...")
    return False


def find_chat_files():
    """Find supported chat files in current directory."""
    if not ConversionEngine:
        # Fallback to CSV only
        csv_files = list(Path('.').glob('*.csv'))
        return [f.name for f in csv_files]

    engine = ConversionEngine()
    formats = engine.list_supported_formats()

    chat_files = []
    extensions = set()

    # Collect extensions
    for fmt in formats['input']:
        extensions.add(fmt)

    # Find files with supported extensions
    for ext in extensions:
        for pattern in [f'*.{ext}', f'*.{ext.upper()}']:
            chat_files.extend(list(Path('.').glob(pattern)))

    return sorted([f.name for f in chat_files])


def check_chat_files():
    """Check for chat files and display them."""
    chat_files = find_chat_files()

    if not chat_files:
        print(f"{colors.YELLOW}⚠️  No chat files found in current directory!{colors.NC}")
        print()
        print(f"{colors.CYAN}Supported formats:{colors.NC}")
        if ConversionEngine:
            engine = ConversionEngine()
            formats = engine.list_supported_formats()
            input_formats = ', '.join(formats['input'][:5]) + '...'
            print(f"  Input: {input_formats}")
        else:
            print("  CSV, JSON, SQLite, Excel, Text")
        print()
        print(f"{colors.YELLOW}Please add a supported chat file and try again.{colors.NC}")
        print()
        input("Press Enter to continue...")
        return False

    print(f"{colors.GREEN}✓ Found {len(chat_files)} chat file(s):{colors.NC}")
    for file in chat_files[:10]:  # Show first 10
        print(f"  {colors.CYAN}• {file}{colors.NC}")
    if len(chat_files) > 10:
        print(f"  {colors.YELLOW}... and {len(chat_files) - 10} more{colors.NC}")
    print()
    return True


def select_file(allow_multiple=False):
    """Interactive file selection."""
    chat_files = find_chat_files()

    if not chat_files:
        return None

    if len(chat_files) == 1:
        print(f"{colors.GREEN}Using: {chat_files[0]}{colors.NC}")
        return chat_files[0]

    print(f"{colors.CYAN}Select input file(s):{colors.NC}")
    for i, file in enumerate(chat_files, 1):
        print(f"  {colors.GREEN}{i}{colors.NC}) {file}")
    if allow_multiple and len(chat_files) > 1:
        print(f"  {colors.GREEN}0{colors.NC}) {colors.BOLD}Process ALL files{colors.NC}")
    print()

    while True:
        if allow_multiple:
            choice = input(f"{colors.YELLOW}Enter file number [0-{len(chat_files)} or 'all']: {colors.NC}").strip().lower()
        else:
            choice = input(f"{colors.YELLOW}Enter file number [1-{len(chat_files)}]: {colors.NC}").strip()

        if choice in ['0', 'all'] and allow_multiple:
            return 'ALL'

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(chat_files):
                return chat_files[idx]
            print(f"{colors.RED}Invalid choice!{colors.NC}")
        except ValueError:
            print(f"{colors.RED}Please enter a number!{colors.NC}")


def select_output_format(engine):
    """Interactive output format selection."""
    formats = engine.list_supported_formats()
    output_formats = formats['output']

    print(f"{colors.CYAN}Select output format:{colors.NC}")

    # Group formats nicely
    format_display = {
        'html': '🌐 HTML (Web page)',
        'md': '📝 Markdown',
        'markdown': '📝 Markdown',
        'json': '📋 JSON',
        'txt': '📄 Text',
        'text': '📄 Text',
        'pdf': '📑 PDF',
        'docx': '📘 Word Document',
        'doc': '📘 Word Document',
        'db': '🗄️  SQLite Database',
        'sqlite': '🗄️  SQLite Database',
        'xmind': '🧠 XMind Map'
    }

    shown_formats = []
    for fmt in output_formats:
        if fmt not in shown_formats:
            shown_formats.append(fmt)

    for i, fmt in enumerate(shown_formats, 1):
        display = format_display.get(fmt, fmt.upper())
        print(f"  {colors.GREEN}{i}{colors.NC}) {display}")
    print()

    while True:
        choice = input(f"{colors.YELLOW}Enter format number [1-{len(shown_formats)}]: {colors.NC}").strip()
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(shown_formats):
                selected_format = shown_formats[idx]

                # XMind compatibility warning
                if selected_format == 'xmind':
                    print()
                    print(f"{colors.YELLOW}╔══════════════════════════════════════════════════════════════════╗{colors.NC}")
                    print(f"{colors.YELLOW}║  ⚠️  XMind Compatibility Warning                                ║{colors.NC}")
                    print(f"{colors.YELLOW}╠══════════════════════════════════════════════════════════════════╣{colors.NC}")
                    print(f"{colors.YELLOW}║{colors.NC}  Generated .xmind files use {colors.BOLD}XMind 8 format{colors.NC} (2020/2021 compatible) {colors.YELLOW}║{colors.NC}")
                    print(f"{colors.YELLOW}║{colors.NC}  They will {colors.RED}{colors.BOLD}NOT{colors.NC} open in XMind 2022 or newer versions!            {colors.YELLOW}║{colors.NC}")
                    print(f"{colors.YELLOW}║{colors.NC}                                                                  {colors.YELLOW}║{colors.NC}")
                    print(f"{colors.YELLOW}║{colors.NC}  📥 Download XMind 8 (free): {colors.CYAN}xmind.com/download/xmind8{colors.NC}   {colors.YELLOW}║{colors.NC}")
                    print(f"{colors.YELLOW}║{colors.NC}     Platforms: Windows, macOS, Linux                            {colors.YELLOW}║{colors.NC}")
                    print(f"{colors.YELLOW}╚══════════════════════════════════════════════════════════════════╝{colors.NC}")
                    print()

                return selected_format
            print(f"{colors.RED}Invalid choice!{colors.NC}")
        except ValueError:
            print(f"{colors.RED}Please enter a number!{colors.NC}")


def run_interactive_conversion():
    """Run interactive conversion using ConversionEngine."""
    print_header()
    print(f"{colors.CYAN}{colors.BOLD}Interactive Conversion{colors.NC}")
    print()

    if not ConversionEngine:
        print(f"{colors.RED}✗ ConversionEngine not available!{colors.NC}")
        print(f"{colors.YELLOW}Please check your installation.{colors.NC}")
        print()
        input("Press Enter to continue...")
        return

    if not check_chat_files():
        return

    # Select input file
    input_file = select_file()
    if not input_file:
        return

    print()

    # Initialize engine
    engine = ConversionEngine()

    # Select output format
    output_format = select_output_format(engine)

    # Generate output filename
    input_path = Path(input_file)
    output_file = str(input_path.with_suffix(f'.{output_format}'))

    print()
    print(f"{colors.CYAN}Converting...{colors.NC}")
    print(f"  Input:  {input_file}")
    print(f"  Output: {output_file}")
    print()

    try:
        result = engine.convert(input_file, output_file, output_format)

        if result.success:
            print(f"{colors.GREEN}✓ Conversion successful!{colors.NC}")
            print(f"  Output: {result.output_file}")
            if result.warnings:
                print(f"{colors.YELLOW}  Warnings: {len(result.warnings)}{colors.NC}")
        else:
            print(f"{colors.RED}✗ Conversion failed!{colors.NC}")
            if result.errors:
                print(f"  Errors:")
                for error in result.errors[:3]:
                    print(f"    • {error}")

    except Exception as e:
        print(f"{colors.RED}✗ Error: {e}{colors.NC}")
        import traceback
        traceback.print_exc()

    print()
    input("Press Enter to continue...")


def run_analytics():
    """Run analytics on a chat file."""
    print_header()
    print(f"{colors.CYAN}{colors.BOLD}Chat Analytics{colors.NC}")
    print()

    if not ConversionEngine or not AnalyticsEngine:
        print(f"{colors.RED}✗ Analytics not available!{colors.NC}")
        print(f"{colors.YELLOW}Please check your installation.{colors.NC}")
        print()
        input("Press Enter to continue...")
        return

    if not check_chat_files():
        return

    # Select input file(s) - allow multiple
    selection = select_file(allow_multiple=True)
    if not selection:
        return

    print()

    # Process all files or single file
    files_to_process = []
    if selection == 'ALL':
        files_to_process = find_chat_files()
        print(f"{colors.CYAN}Analyzing ALL {len(files_to_process)} files...{colors.NC}")
    else:
        files_to_process = [selection]
        print(f"{colors.CYAN}Analyzing: {selection}{colors.NC}")

    print()

    # Initialize engines once
    engine = ConversionEngine()
    analytics = AnalyticsEngine(use_ai=False)

    # Process each file
    for file_index, input_file in enumerate(files_to_process, 1):
        try:
            # Show which file we're processing if multiple
            if len(files_to_process) > 1:
                print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
                print(f"{colors.BOLD}File {file_index}/{len(files_to_process)}: {input_file}{colors.NC}")
                print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
                print()

            # Parse conversation
            parser = engine._get_parser(input_file)
            conversation = parser.parse(input_file)

            # Run analytics (keyword-based, no AI)
            results = analytics.analyze(conversation)

            # Display results
            print(f"{colors.GREEN}✓ Analysis complete!{colors.NC}")
            print()

            # Basic Stats
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
            print(f"{colors.BOLD}{colors.CYAN}📊 BASIC STATISTICS{colors.NC}")
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

        # Sentiment
        if 'sentiment' in results and 'error' not in results['sentiment']:
            sentiment = results['sentiment']

            # Show method used
            method = sentiment.get('method', 'unknown')
            method_display = {
                'ensemble': 'Ensemble (VADER + TextBlob + Keywords)',
                'vader': 'VADER (Social Media Optimized)',
                'textblob': 'TextBlob (Polarity Analysis)',
                'ai': 'Groq AI (Advanced)',
                'keyword': 'Keyword-based (Basic)'
            }
            print(f"{colors.BOLD}Sentiment:{colors.NC} {sentiment['overall_sentiment'].upper()}")
            print(f"  Score: {sentiment['sentiment_score']:.2f} (range: -1.0 to +1.0)")
            print(f"  Method: {method_display.get(method, method)}")

            # Show polarity/subjectivity if available
            if 'avg_polarity' in sentiment:
                print(f"  Avg Polarity: {sentiment['avg_polarity']:.2f} (TextBlob)")
            if 'avg_subjectivity' in sentiment:
                print(f"  Avg Subjectivity: {sentiment['avg_subjectivity']:.2f} (0.0=objective, 1.0=subjective)")

            # Show score distribution if available
            if 'score_distribution' in sentiment:
                dist = sentiment['score_distribution']
                print(f"  Distribution:")
                print(f"    Very Negative: {dist.get('very_negative', 0)}")
                print(f"    Negative: {dist.get('negative', 0)}")
                print(f"    Neutral: {dist.get('neutral', 0)}")
                print(f"    Positive: {dist.get('positive', 0)}")
                print(f"    Very Positive: {dist.get('very_positive', 0)}")
            print()

        # Topics
        if 'topics' in results and 'error' not in results['topics']:
            topics = results['topics']['main_topics'][:5]
            print(f"{colors.BOLD}Top Topics:{colors.NC} {', '.join(topics)}")
            print()

        # Activity
        if 'activity' in results and 'error' not in results['activity']:
            activity = results['activity']
            print(f"{colors.BOLD}Total Messages:{colors.NC} {activity['total_messages']}")
            print(f"{colors.BOLD}Participants:{colors.NC} {activity.get('num_participants', 'N/A')}")
            most_active = activity.get('most_active_participant', {})
            if most_active.get('name'):
                print(f"{colors.BOLD}Most Active:{colors.NC} {most_active['name']} ({most_active['message_count']} messages)")
            print()

        # Words
        if 'word_frequency' in results and 'error' not in results['word_frequency']:
            words = results['word_frequency']
            print(f"{colors.BOLD}Total Words:{colors.NC} {words['total_words']}")
            print(f"{colors.BOLD}Unique Words:{colors.NC} {words['unique_words']}")
            print(f"{colors.BOLD}Vocabulary Diversity:{colors.NC} {words['vocabulary_diversity']:.2%}")
            print()

        # Phase 1: Enhanced Temporal Metrics
        if 'activity' in results and 'error' not in results['activity']:
            activity = results['activity']

            # Frequency patterns
            if 'frequency_patterns' in activity:
                freq = activity['frequency_patterns']
                print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
                print(f"{colors.BOLD}{colors.CYAN}📈 TEMPORAL ANALYSIS (Phase 1){colors.NC}")
                print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

                if 'avg_interval_minutes' in freq:
                    avg_min = freq['avg_interval_minutes']
                    if avg_min < 60:
                        print(f"{colors.BOLD}Avg Response Time:{colors.NC} {avg_min:.1f} minutes")
                    else:
                        print(f"{colors.BOLD}Avg Response Time:{colors.NC} {avg_min/60:.1f} hours")

                if 'frequency_distribution' in freq:
                    dist = freq['frequency_distribution']
                    print(f"{colors.BOLD}Message Frequency:{colors.NC}")
                    print(f"  Very High (< 1 min): {dist.get('very_high', 0)}")
                    print(f"  High (1-10 min): {dist.get('high', 0)}")
                    print(f"  Medium (10-60 min): {dist.get('medium', 0)}")
                    print(f"  Low (1-6 hrs): {dist.get('low', 0)}")
                    print(f"  Very Low (> 6 hrs): {dist.get('very_low', 0)}")
                print()

            # Burst periods
            if 'burst_periods' in activity and activity['burst_periods']:
                bursts = activity['burst_periods'][:3]  # Top 3
                print(f"{colors.BOLD}🔥 Burst Periods:{colors.NC} {len(activity['burst_periods'])} detected")
                for i, burst in enumerate(bursts, 1):
                    print(f"  {i}. {burst['messages']} messages in {burst['duration_minutes']:.1f} min ({burst['start_time']})")
                print()

            # Dormant periods
            if 'dormant_periods' in activity and activity['dormant_periods']:
                dormant = activity['dormant_periods'][:3]  # Top 3
                print(f"{colors.BOLD}💤 Dormant Periods:{colors.NC} {len(activity['dormant_periods'])} detected")
                for i, period in enumerate(dormant, 1):
                    print(f"  {i}. {period['duration_hours']:.1f} hours gap")
                print()

        # Phase 2: Content Analysis
        if 'content_analysis' in results and 'error' not in results['content_analysis']:
            content = results['content_analysis']

            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
            print(f"{colors.BOLD}{colors.CYAN}🔍 CONTENT ANALYSIS (Phase 2){colors.NC}")
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

            # Statement types
            if 'statement_types' in content:
                stmt = content['statement_types']
                total_stmt = sum(stmt.get('statement_counts', {}).values())
                counts = stmt.get('statement_counts', {})
                if total_stmt > 0:
                    print(f"{colors.BOLD}Statement Types:{colors.NC}")
                    print(f"  Questions: {counts.get('questions', 0)} ({counts.get('questions', 0)/total_stmt*100:.1f}%)")
                    print(f"  Commands: {counts.get('commands', 0)} ({counts.get('commands', 0)/total_stmt*100:.1f}%)")
                    print(f"  Assertions: {counts.get('assertions', 0)} ({counts.get('assertions', 0)/total_stmt*100:.1f}%)")
                    print(f"  Exclamations: {counts.get('exclamations', 0)} ({counts.get('exclamations', 0)/total_stmt*100:.1f}%)")
                    print()

            # Language complexity
            if 'language_complexity' in content:
                lang = content['language_complexity']
                print(f"{colors.BOLD}Language Complexity:{colors.NC}")
                print(f"  Avg Word Length: {lang.get('avg_word_length', 0):.1f} chars")
                print(f"  Avg Sentence Length: {lang.get('avg_sentence_length', 0):.1f} words")
                print(f"  Reading Level: Grade {lang.get('reading_level', 0):.1f}")
                print()

            # Emotional intensity
            if 'emotional_intensity' in content:
                emo = content['emotional_intensity']
                print(f"{colors.BOLD}Emotional Intensity:{colors.NC}")
                print(f"  High Intensity Messages: {emo.get('high_intensity_count', 0)}")
                print(f"  Avg Intensity: {emo.get('avg_intensity', 0):.2f}")
                print()

        # Phase 3: Network Graph Analysis
        if 'network_graph' in results and results['network_graph'].get('available'):
            network = results['network_graph']
            stats = network.get('network_stats', {})

            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
            print(f"{colors.BOLD}{colors.CYAN}🕸️  NETWORK ANALYSIS (Phase 3){colors.NC}")
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

            print(f"{colors.BOLD}Network Statistics:{colors.NC}")
            print(f"  Nodes (Participants): {stats.get('total_nodes', 0)}")
            print(f"  Connections: {stats.get('total_edges', 0)}")
            print(f"  Density: {stats.get('density', 0):.2%}")
            print(f"  Communities: {stats.get('num_communities', 0)}")
            print()

            print(f"{colors.BOLD}Key Participants:{colors.NC}")
            if stats.get('most_central'):
                print(f"  🎯 Most Central: {stats['most_central']}")
            if stats.get('most_responded_to'):
                print(f"  💬 Most Responded To: {stats['most_responded_to']}")
            if stats.get('most_responsive'):
                print(f"  ↩️  Most Responsive: {stats['most_responsive']}")
            print()

            # Top connections
            if network.get('edges'):
                edges = network['edges'][:5]  # Top 5
                print(f"{colors.BOLD}Top Connections:{colors.NC}")
                for i, edge in enumerate(edges, 1):
                    print(f"  {i}. {edge['from']} → {edge['to']}: {edge['weight']} responses")
                print()

            # Communities
            if stats.get('num_communities', 1) > 1 and stats.get('communities'):
                print(f"{colors.BOLD}Communities Detected:{colors.NC}")
                for i, community in enumerate(stats['communities'][:3], 1):
                    members = ', '.join(community)
                    print(f"  Group {i}: {members}")
                print()

        # Call Log specific analytics
        if 'call_log' in results and results['call_log'].get('is_call_log'):
            call_data = results['call_log']

            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
            print(f"{colors.BOLD}{colors.CYAN}📞 CALL LOG ANALYSIS{colors.NC}")
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

            print(f"{colors.BOLD}Call Statistics:{colors.NC}")
            print(f"  Total Calls: {call_data.get('total_calls', 0)}")
            print(f"  Completed: {call_data.get('completed_calls', 0)}")
            print(f"  Missed: {call_data.get('missed_calls', 0)} ({call_data.get('missed_call_percentage', 0)}%)")
            print(f"  Total Duration: {call_data.get('total_duration_minutes', 0):.0f} minutes")
            print()

            direction = call_data.get('incoming_vs_outgoing', {})
            if direction:
                print(f"{colors.BOLD}Call Direction:{colors.NC}")
                print(f"  Incoming: {direction.get('incoming', 0)} ({direction.get('incoming_percentage', 0)}%)")
                print(f"  Outgoing: {direction.get('outgoing', 0)} ({direction.get('outgoing_percentage', 0)}%)")
                print()

            # Summary
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")
            print(f"{colors.CYAN}⏱️  Analysis completed in {results['processing_time']:.2f}s{colors.NC}")
            print(f"{colors.PURPLE}{'═' * 60}{colors.NC}")

            # Add spacing between files if processing multiple
            if len(files_to_process) > 1 and file_index < len(files_to_process):
                print()
                print()

        except Exception as e:
            print(f"{colors.RED}✗ Analysis failed for {input_file}: {e}{colors.NC}")
            import traceback
            traceback.print_exc()
            # Continue with next file if processing multiple
            if len(files_to_process) > 1:
                print()
                continue

    print()
    input("Press Enter to continue...")


def show_formats():
    """Display all supported formats."""
    print_header()
    print(f"{colors.CYAN}{colors.BOLD}Supported Formats{colors.NC}")
    print()

    if not ConversionEngine:
        print(f"{colors.RED}✗ ConversionEngine not available!{colors.NC}")
        print()
        input("Press Enter to continue...")
        return

    engine = ConversionEngine()
    formats = engine.list_supported_formats()

    print(f"{colors.GREEN}Input Formats ({len(formats['input'])}):{colors.NC}")
    print(f"  {', '.join(formats['input'])}")
    print()

    print(f"{colors.GREEN}Output Formats ({len(formats['output'])}):{colors.NC}")
    print(f"  {', '.join(formats['output'])}")
    print()

    input("Press Enter to continue...")


def show_help():
    """Display help information."""
    print_header()
    print(f"{colors.CYAN}{colors.BOLD}How to Use ChatConvert Toolkit{colors.NC}")
    print()
    print(f"{colors.YELLOW}1. Supported Input Formats (10+):{colors.NC}")
    print("   • CSV, JSON, Excel (XLS/XLSX)")
    print("   • Discord, Slack, Telegram, Messenger")
    print("   • WhatsApp, SMS, iMessage")
    print("   • SQLite databases, Text files")
    print()
    print(f"{colors.YELLOW}2. Output Formats (8):{colors.NC}")
    print("   • HTML - Beautiful web page with styling")
    print("   • Markdown - GitHub-compatible markdown")
    print("   • PDF - Printable document")
    print("   • DOCX - Microsoft Word document")
    print("   • JSON - Machine-readable format")
    print("   • SQLite - Searchable database")
    print("   • XMind - Mind map visualization")
    print("   • Text - Plain text format")
    print()
    print(f"{colors.YELLOW}3. Features:{colors.NC}")
    print("   • Automatic format detection")
    print("   • AI-powered analytics (sentiment, topics)")
    print("   • Batch conversion support")
    print("   • Web interface with REST API")
    print("   • Cross-platform (Windows, macOS, Linux)")
    print()
    print(f"{colors.YELLOW}4. Usage:{colors.NC}")
    print("   • Place chat file in this directory")
    print("   • Choose option 1 for interactive conversion")
    print("   • Choose option 2 for analytics")
    print("   • Use option 6 to install dependencies")
    print()
    input("Press Enter to continue...")


def show_menu():
    """Display main menu and get user choice."""
    print_header()

    print(f"{colors.CYAN}{colors.BOLD}Main Menu:{colors.NC}")
    print()
    print(f"  {colors.GREEN}1{colors.NC}) 🔄 Convert Chat File (Interactive)")
    print(f"  {colors.GREEN}2{colors.NC}) 📊 Analyze Chat File")
    print(f"  {colors.GREEN}3{colors.NC}) 📋 Show Supported Formats")
    print()
    print(f"  {colors.BLUE}4{colors.NC}) 📦 Install/Check Dependencies")
    print(f"  {colors.BLUE}5{colors.NC}) ❓ Help")
    print()
    print(f"  {colors.RED}0{colors.NC}) 🚪 Exit")
    print()

    choice = input(f"{colors.YELLOW}Enter your choice [0-5]: {colors.NC}").strip()
    return choice


def main():
    """Main program loop."""
    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Wait a moment to show version info
    import time
    time.sleep(1)

    # Main loop
    while True:
        choice = show_menu()

        if choice == '1':
            run_interactive_conversion()

        elif choice == '2':
            run_analytics()

        elif choice == '3':
            show_formats()

        elif choice == '4':
            install_dependencies()

        elif choice == '5':
            show_help()

        elif choice == '0':
            print_header()
            print(f"{colors.GREEN}Thank you for using ChatConvert Toolkit!{colors.NC}")
            print(f"{colors.CYAN}Visit: https://github.com/shadowdevnotreal/ChatConvert-Toolkit{colors.NC}")
            print()
            sys.exit(0)

        else:
            print(f"{colors.RED}Invalid option! Please try again.{colors.NC}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(f"{colors.YELLOW}Program interrupted by user.{colors.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"{colors.RED}Unexpected error: {e}{colors.NC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
