import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from trading_bot import TradingBot
from config import Config

class StockBotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Advanced Stock Market Bot - Indian Markets")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize trading bot
        self.bot = TradingBot()
        self.is_logged_in = True  # Set to True since we're not using login anymore
        
        # Setup GUI
        self.setup_gui()
        

    
    def setup_gui(self):
        """Setup the main GUI"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', background='#1e1e1e', foreground='#ffffff', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', background='#2d2d2d', foreground='#ffffff', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', background='#2d2d2d', foreground='#cccccc', font=('Arial', 10))
        
        # Main title
        title_label = ttk.Label(self.root, text="🚀 Advanced Stock Market Bot", style='Title.TLabel')
        title_label.pack(pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_analysis_tab()
        self.create_trading_tab()
        self.create_portfolio_tab()
        self.create_risk_management_tab()
        self.create_settings_tab()
    
    def create_risk_management_tab(self):
        """Create risk management tab"""
        risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(risk_frame, text="🛡️ Risk Management")
        
        # Risk management content
        risk_container = ttk.Frame(risk_frame)
        risk_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Risk parameters
        risk_params_frame = ttk.LabelFrame(risk_container, text="Risk Parameters", padding=10)
        risk_params_frame.pack(fill='x', pady=10)
        
        # Position size calculator
        position_frame = ttk.LabelFrame(risk_container, text="Position Size Calculator", padding=10)
        position_frame.pack(fill='x', pady=10)
        
        ttk.Label(position_frame, text="Account Size (₹):", style='Info.TLabel').pack(side='left', padx=5)
        self.account_size_entry = ttk.Entry(position_frame, width=15)
        self.account_size_entry.pack(side='left', padx=5)
        self.account_size_entry.insert(0, "100000")
        
        ttk.Label(position_frame, text="Risk Per Trade (%):", style='Info.TLabel').pack(side='left', padx=5)
        self.risk_per_trade_entry = ttk.Entry(position_frame, width=10)
        self.risk_per_trade_entry.pack(side='left', padx=5)
        self.risk_per_trade_entry.insert(0, "1")
        
        ttk.Label(position_frame, text="Stop Loss (%):", style='Info.TLabel').pack(side='left', padx=5)
        self.stop_loss_pct_entry = ttk.Entry(position_frame, width=10)
        self.stop_loss_pct_entry.pack(side='left', padx=5)
        self.stop_loss_pct_entry.insert(0, "2")
        
        calculate_btn = ttk.Button(position_frame, text="Calculate Position Size", command=self.calculate_position_size)
        calculate_btn.pack(side='left', padx=5)
        
        # Position size result
        self.position_size_result = ttk.Label(position_frame, text="", style='Info.TLabel')
        self.position_size_result.pack(pady=5)
        
        # Risk management tips
        tips_frame = ttk.LabelFrame(risk_container, text="Risk Management Tips", padding=10)
        tips_frame.pack(fill='both', expand=True, pady=10)
        
        # Tips text area
        tips_text = """
🛡️ ESSENTIAL RISK MANAGEMENT RULES:

1. POSITION SIZING:
   • Never risk more than 1-2% of your capital per trade
   • Use the position size calculator above
   • Adjust based on signal strength

2. STOP LOSS:
   • Always use stop loss - no exceptions
   • Place stop loss below support (for buys) or above resistance (for sells)
   • Use ATR-based stops for volatility adjustment

3. TAKE PROFIT:
   • Aim for minimum 2:1 risk-reward ratio
   • Set multiple profit targets
   • Use trailing stops for remaining position

4. ENTRY STRATEGY:
   • Enter in multiple lots at different levels
   • Wait for confirmation before full position
   • Avoid chasing the market

5. EXIT STRATEGY:
   • Have a clear exit plan before entering
   • Use partial exits at resistance/support levels
   • Don't let profits turn into losses

6. EMOTIONAL CONTROL:
   • Stick to your trading plan
   • Don't revenge trade after losses
   • Keep a trading journal

7. MARKET CONDITIONS:
   • Avoid trading in high volatility without adjustment
   • Consider market trend before taking trades
   • Don't fight the trend

8. PORTFOLIO MANAGEMENT:
   • Diversify across different stocks
   • Don't put all eggs in one basket
   • Regular portfolio review
        """
        
        self.tips_text_widget = tk.Text(tips_frame, height=20, width=80, wrap=tk.WORD)
        self.tips_text_widget.pack(fill='both', expand=True)
        self.tips_text_widget.insert('1.0', tips_text)
        self.tips_text_widget.config(state='disabled')
    

    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        
        # Dashboard content
        dashboard_container = ttk.Frame(dashboard_frame)
        dashboard_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Market status
        status_frame = ttk.LabelFrame(dashboard_container, text="Market Status", padding=10)
        status_frame.pack(fill='x', pady=10)
        
        self.market_status_label = ttk.Label(status_frame, text="Market: Closed", style='Info.TLabel')
        self.market_status_label.pack()
        
        # Portfolio summary
        portfolio_frame = ttk.LabelFrame(dashboard_container, text="Portfolio Summary", padding=10)
        portfolio_frame.pack(fill='x', pady=10)
        
        self.portfolio_summary = ttk.Label(portfolio_frame, text="Portfolio data not available", style='Info.TLabel')
        self.portfolio_summary.pack()
        
        # Recent signals
        signals_frame = ttk.LabelFrame(dashboard_container, text="Recent Signals", padding=10)
        signals_frame.pack(fill='both', expand=True, pady=10)
        
        # Signals treeview
        columns = ('Symbol', 'Type', 'Indicator', 'Strength', 'Time')
        self.signals_tree = ttk.Treeview(signals_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.signals_tree.heading(col, text=col)
            self.signals_tree.column(col, width=100)
        
        self.signals_tree.pack(fill='both', expand=True)
        
        # Refresh button
        refresh_btn = ttk.Button(dashboard_container, text="Refresh Dashboard", command=self.refresh_dashboard)
        refresh_btn.pack(pady=10)
    
    def create_analysis_tab(self):
        """Create analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="📈 Analysis")
        
        # Analysis content
        analysis_container = ttk.Frame(analysis_frame)
        analysis_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Symbol selection
        symbol_frame = ttk.LabelFrame(analysis_container, text="Symbol Analysis", padding=10)
        symbol_frame.pack(fill='x', pady=10)
        
        ttk.Label(symbol_frame, text="Symbol:", style='Info.TLabel').pack(side='left', padx=5)
        self.symbol_entry = ttk.Entry(symbol_frame, width=20)
        self.symbol_entry.pack(side='left', padx=5)
        
        analyze_btn = ttk.Button(symbol_frame, text="Analyze", command=self.analyze_symbol)
        analyze_btn.pack(side='left', padx=5)
        
        # Chart frame
        chart_frame = ttk.LabelFrame(analysis_container, text="Technical Analysis Chart", padding=10)
        chart_frame.pack(fill='both', expand=True, pady=10)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Analysis results
        results_frame = ttk.LabelFrame(analysis_container, text="Analysis Results", padding=10)
        results_frame.pack(fill='x', pady=10)
        
        self.analysis_results = ttk.Label(results_frame, text="Select a symbol to analyze", style='Info.TLabel')
        self.analysis_results.pack()
        
        # Risk management results
        risk_results_frame = ttk.LabelFrame(analysis_container, text="Risk Management Analysis", padding=10)
        risk_results_frame.pack(fill='x', pady=10)
        
        self.risk_results = ttk.Label(risk_results_frame, text="Risk analysis will appear here", style='Info.TLabel')
        self.risk_results.pack()
    
    def create_trading_tab(self):
        """Create trading tab"""
        trading_frame = ttk.Frame(self.notebook)
        self.notebook.add(trading_frame, text="💰 Trading")
        
        # Trading content
        trading_container = ttk.Frame(trading_frame)
        trading_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Watchlist management
        watchlist_frame = ttk.LabelFrame(trading_container, text="Watchlist Management", padding=10)
        watchlist_frame.pack(fill='x', pady=10)
        
        ttk.Label(watchlist_frame, text="Add Symbol:", style='Info.TLabel').pack(side='left', padx=5)
        self.watchlist_entry = ttk.Entry(watchlist_frame, width=20)
        self.watchlist_entry.pack(side='left', padx=5)
        
        add_btn = ttk.Button(watchlist_frame, text="Add", command=self.add_to_watchlist)
        add_btn.pack(side='left', padx=5)
        
        remove_btn = ttk.Button(watchlist_frame, text="Remove", command=self.remove_from_watchlist)
        remove_btn.pack(side='left', padx=5)
        
        # Watchlist display
        watchlist_display_frame = ttk.LabelFrame(trading_container, text="Current Watchlist", padding=10)
        watchlist_display_frame.pack(fill='x', pady=10)
        
        self.watchlist_display = ttk.Label(watchlist_display_frame, text="No symbols in watchlist", style='Info.TLabel')
        self.watchlist_display.pack()
        
        # Signal monitoring controls
        signal_monitoring_frame = ttk.LabelFrame(trading_container, text="Signal Monitoring", padding=10)
        signal_monitoring_frame.pack(fill='x', pady=10)
        
        self.signal_monitoring_status = ttk.Label(signal_monitoring_frame, text="Signal Monitoring: Stopped", style='Info.TLabel')
        self.signal_monitoring_status.pack()
        
        start_monitoring_btn = ttk.Button(signal_monitoring_frame, text="Start Monitoring", command=self.start_signal_monitoring)
        start_monitoring_btn.pack(side='left', padx=5, pady=5)
        
        stop_monitoring_btn = ttk.Button(signal_monitoring_frame, text="Stop Monitoring", command=self.stop_signal_monitoring)
        stop_monitoring_btn.pack(side='left', padx=5, pady=5)
        
        # Signal analysis
        signal_analysis_frame = ttk.LabelFrame(trading_container, text="Signal Analysis", padding=10)
        signal_analysis_frame.pack(fill='x', pady=10)
        
        analyze_all_btn = ttk.Button(signal_analysis_frame, text="Analyze All Symbols", command=self.analyze_all_symbols)
        analyze_all_btn.pack(side='left', padx=5, pady=5)
        
        generate_report_btn = ttk.Button(signal_analysis_frame, text="Generate Signal Report", command=self.generate_signal_report)
        generate_report_btn.pack(side='left', padx=5, pady=5)
        
        get_alerts_btn = ttk.Button(signal_analysis_frame, text="Get Signal Alerts", command=self.get_signal_alerts)
        get_alerts_btn.pack(side='left', padx=5, pady=5)
    
    def create_portfolio_tab(self):
        """Create portfolio tab"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="💼 Portfolio")
        
        # Portfolio content
        portfolio_container = ttk.Frame(portfolio_frame)
        portfolio_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Portfolio summary
        summary_frame = ttk.LabelFrame(portfolio_container, text="Portfolio Summary", padding=10)
        summary_frame.pack(fill='x', pady=10)
        
        self.portfolio_details = ttk.Label(summary_frame, text="Not logged in", style='Info.TLabel')
        self.portfolio_details.pack()
        
        # Trade history
        history_frame = ttk.LabelFrame(portfolio_container, text="Trade History", padding=10)
        history_frame.pack(fill='both', expand=True, pady=10)
        
        # Trade history treeview
        columns = ('Symbol', 'Side', 'Quantity', 'Price', 'Time', 'Status')
        self.trade_history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.trade_history_tree.heading(col, text=col)
            self.trade_history_tree.column(col, width=100)
        
        self.trade_history_tree.pack(fill='both', expand=True)
        
        # Export button
        export_btn = ttk.Button(portfolio_container, text="Export Portfolio", command=self.export_portfolio)
        export_btn.pack(pady=10)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings content
        settings_container = ttk.Frame(settings_frame)
        settings_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Risk management
        risk_frame = ttk.LabelFrame(settings_container, text="Risk Management", padding=10)
        risk_frame.pack(fill='x', pady=10)
        
        ttk.Label(risk_frame, text="Max Position Size (%):", style='Info.TLabel').pack(anchor='w', pady=5)
        self.max_position_entry = ttk.Entry(risk_frame, width=20)
        self.max_position_entry.pack(anchor='w', pady=5)
        self.max_position_entry.insert(0, str(self.bot.risk_management['max_position_size'] * 100))
        
        ttk.Label(risk_frame, text="Stop Loss (%):", style='Info.TLabel').pack(anchor='w', pady=5)
        self.stop_loss_entry = ttk.Entry(risk_frame, width=20)
        self.stop_loss_entry.pack(anchor='w', pady=5)
        self.stop_loss_entry.insert(0, str(self.bot.risk_management['stop_loss_pct'] * 100))
        
        ttk.Label(risk_frame, text="Take Profit (%):", style='Info.TLabel').pack(anchor='w', pady=5)
        self.take_profit_entry = ttk.Entry(risk_frame, width=20)
        self.take_profit_entry.pack(anchor='w', pady=5)
        self.take_profit_entry.insert(0, str(self.bot.risk_management['take_profit_pct'] * 100))
        
        save_risk_btn = ttk.Button(risk_frame, text="Save Risk Settings", command=self.save_risk_settings)
        save_risk_btn.pack(pady=10)
        
        # Data management
        data_frame = ttk.LabelFrame(settings_container, text="Data Management", padding=10)
        data_frame.pack(fill='x', pady=10)
        
        update_data_btn = ttk.Button(data_frame, text="Update All Data", command=self.update_all_data)
        update_data_btn.pack(side='left', padx=5, pady=5)
        
        cleanup_btn = ttk.Button(data_frame, text="Cleanup Old Data", command=self.cleanup_data)
        cleanup_btn.pack(side='left', padx=5, pady=5)
        
        # Reports
        reports_frame = ttk.LabelFrame(settings_container, text="Reports", padding=10)
        reports_frame.pack(fill='x', pady=10)
        
        generate_report_btn = ttk.Button(reports_frame, text="Generate Report", command=self.generate_report)
        generate_report_btn.pack(pady=5)
    

    

    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        try:
            if not self.is_logged_in:
                return
            
            # Update market status
            if self.bot.config.is_market_open():
                self.market_status_label.config(text="Market: Open")
            else:
                self.market_status_label.config(text="Market: Closed")
            
            # Update portfolio summary
            portfolio = self.bot.get_portfolio_summary()
            if portfolio:
                summary_text = f"Total Value: ₹{portfolio['total_value']:,.2f}\nTotal P&L: ₹{portfolio['total_pnl']:,.2f}"
                self.portfolio_summary.config(text=summary_text)
            
            # Update recent signals
            signals = self.bot.get_recent_signals(days=7)
            self.signals_tree.delete(*self.signals_tree.get_children())
            
            for _, signal in signals.iterrows():
                self.signals_tree.insert('', 'end', values=(
                    signal['symbol'],
                    signal['signal_type'],
                    signal['indicator'],
                    signal['strength'],
                    signal['timestamp']
                ))
            
            # Update watchlist display
            watchlist_text = ", ".join(self.bot.watchlist) if self.bot.watchlist else "No symbols in watchlist"
            self.watchlist_display.config(text=watchlist_text)
            
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
    
    def analyze_symbol(self):
        """Analyze a symbol"""
        try:
            symbol = self.symbol_entry.get().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a symbol")
                return
            
            def analysis_thread():
                try:
                    # Add to watchlist if not already there
                    if symbol not in self.bot.watchlist:
                        self.bot.add_to_watchlist(symbol)
                    
                    # Analyze symbol
                    signals = self.bot.analyze_symbol(symbol)
                    
                    # Update results
                    if signals:
                        results_text = f"Generated {len(signals)} signals:\n"
                        risk_text = ""
                        
                        for signal in signals:
                            results_text += f"• {signal['type']} - {signal['indicator']} ({signal['strength']})\n"
                            
                            # Get detailed signal analysis with risk management
                            signal_details = self.bot.get_signal_details(symbol, signal)
                            if signal_details and 'risk_management' in signal_details:
                                rm = signal_details['risk_management']
                                
                                risk_text += f"\n📊 {signal['type']} SIGNAL ANALYSIS:\n"
                                risk_text += f"Signal Strength: {signal_details.get('signal_strength', 'Unknown')}\n"
                                
                                # Position size
                                if 'position_size' in rm and rm['position_size']:
                                    ps = rm['position_size']
                                    risk_text += f"Position Size: {ps.get('percentage', 0)}% of capital\n"
                                    risk_text += f"Risk Amount: {ps.get('risk_amount', 0)}% of capital\n"
                                
                                # Stop loss
                                if 'stop_loss' in rm and rm['stop_loss'].get('recommended'):
                                    sl = rm['stop_loss']['recommended']
                                    risk_text += f"Stop Loss: ₹{sl['price']} ({sl['distance']}%)\n"
                                
                                # Take profit
                                if 'take_profit' in rm and rm['take_profit'].get('recommended'):
                                    tp = rm['take_profit']['recommended']
                                    risk_text += f"Take Profit: ₹{tp['price']} ({tp['distance']}%)\n"
                                
                                # Risk-reward ratio
                                if 'risk_reward_ratio' in rm and rm['risk_reward_ratio']:
                                    rr = rm['risk_reward_ratio']
                                    risk_text += f"Risk-Reward: {rr.get('ratio', 0)}:1 ({rr.get('recommendation', '')})\n"
                                
                                # Risk tips
                                if 'risk_tips' in rm and rm['risk_tips']:
                                    risk_text += f"Risk Tips: {rm['risk_tips'][0]}\n"
                                
                                # Market conditions
                                if 'market_conditions' in rm:
                                    mc = rm['market_conditions']
                                    risk_text += f"Market Trend: {mc.get('trend', 'Unknown')}\n"
                                    risk_text += f"Volatility: {mc.get('volatility', 'Unknown')}\n"
                                    risk_text += f"Momentum: {mc.get('momentum', 'Unknown')}\n"
                                
                                risk_text += "-" * 50 + "\n"
                    else:
                        results_text = "No signals generated"
                        risk_text = "No risk analysis available"
                    
                    self.analysis_results.config(text=results_text)
                    self.risk_results.config(text=risk_text)
                    
                    # Update chart (simplified)
                    self.update_chart(symbol)
                except Exception as e:
                    messagebox.showerror("Error", f"Analysis error: {e}")
            
            threading.Thread(target=analysis_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing symbol: {e}")
    
    def update_chart(self, symbol):
        """Update the chart with symbol data"""
        try:
            # Get data
            df = self.bot.data_manager.get_latest_data(symbol, days=90)
            
            if df.empty:
                return
            
            # Clear previous chart
            self.ax.clear()
            
            # Plot price data
            self.ax.plot(df['timestamp'], df['close'], label='Close Price')
            
            # Add moving averages if available
            if 'sma_20' in df.columns:
                self.ax.plot(df['timestamp'], df['sma_20'], label='SMA 20', alpha=0.7)
            if 'sma_50' in df.columns:
                self.ax.plot(df['timestamp'], df['sma_50'], label='SMA 50', alpha=0.7)
            
            self.ax.set_title(f'{symbol} Price Chart')
            self.ax.set_xlabel('Date')
            self.ax.set_ylabel('Price')
            self.ax.legend()
            self.ax.tick_params(axis='x', rotation=45)
            
            # Update canvas
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating chart: {e}")
    
    def add_to_watchlist(self):
        """Add symbol to watchlist"""
        try:
            symbol = self.watchlist_entry.get().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a symbol")
                return
            
            success = self.bot.add_to_watchlist(symbol)
            if success:
                self.watchlist_entry.delete(0, tk.END)
                self.refresh_dashboard()
                messagebox.showinfo("Success", f"Added {symbol} to watchlist")
            else:
                messagebox.showerror("Error", f"Failed to add {symbol} to watchlist")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error adding to watchlist: {e}")
    
    def remove_from_watchlist(self):
        """Remove symbol from watchlist"""
        try:
            symbol = self.watchlist_entry.get().upper()
            if not symbol:
                messagebox.showerror("Error", "Please enter a symbol")
                return
            
            success = self.bot.remove_from_watchlist(symbol)
            if success:
                self.watchlist_entry.delete(0, tk.END)
                self.refresh_dashboard()
                messagebox.showinfo("Success", f"Removed {symbol} from watchlist")
            else:
                messagebox.showerror("Error", f"Failed to remove {symbol} from watchlist")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error removing from watchlist: {e}")
    
    def start_signal_monitoring(self):
        """Start signal monitoring"""
        try:
            if not self.is_logged_in:
                messagebox.showerror("Error", "Please login first")
                return
            
            success = self.bot.monitor_signals(interval_minutes=5)
            if success:
                self.signal_monitoring_status.config(text="Signal Monitoring: Running")
                messagebox.showinfo("Success", "Signal monitoring started")
            else:
                messagebox.showerror("Error", "Failed to start signal monitoring")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error starting signal monitoring: {e}")
    
    def stop_signal_monitoring(self):
        """Stop signal monitoring"""
        try:
            success = self.bot.stop_signal_monitoring()
            if success:
                self.signal_monitoring_status.config(text="Signal Monitoring: Stopped")
                messagebox.showinfo("Success", "Signal monitoring stopped")
            else:
                messagebox.showerror("Error", "Failed to stop signal monitoring")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping signal monitoring: {e}")
    
    def analyze_all_symbols(self):
        """Analyze all symbols in watchlist"""
        try:
            if not self.is_logged_in:
                messagebox.showerror("Error", "Please login first")
                return
            
            def analysis_thread():
                try:
                    signals = self.bot.analyze_all_symbols()
                    if signals:
                        messagebox.showinfo("Success", f"Analysis complete! Generated signals for {len(signals)} symbols")
                        self.refresh_dashboard()
                    else:
                        messagebox.showinfo("Info", "No signals generated")
                except Exception as e:
                    messagebox.showerror("Error", f"Analysis error: {e}")
            
            threading.Thread(target=analysis_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing symbols: {e}")
    
    def generate_signal_report(self):
        """Generate signal report"""
        try:
            if not self.is_logged_in:
                messagebox.showerror("Error", "Please login first")
                return
            
            def report_thread():
                try:
                    report = self.bot.generate_signal_report()
                    if report:
                        # Save report to file
                        filename = f"reports/signal_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        import json
                        with open(filename, 'w') as f:
                            json.dump(report, f, indent=2, default=str)
                        
                        messagebox.showinfo("Success", f"Signal report generated and saved to {filename}")
                    else:
                        messagebox.showerror("Error", "Failed to generate signal report")
                except Exception as e:
                    messagebox.showerror("Error", f"Report generation error: {e}")
            
            threading.Thread(target=report_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")
    
    def get_signal_alerts(self):
        """Get signal alerts"""
        try:
            if not self.is_logged_in:
                messagebox.showerror("Error", "Please login first")
                return
            
            alerts = self.bot.get_signal_alerts('STRONG')
            
            if alerts:
                alert_text = f"Found {len(alerts)} strong signals:\n\n"
                for alert in alerts:
                    alert_text += f"• {alert['symbol']} - {alert['signal_type']} ({alert['signal_strength']})\n"
                    alert_text += f"  Reason: {alert['reason']}\n"
                    alert_text += f"  Current Price: ₹{alert['current_price']:.2f}\n"
                    
                    # Add risk management info
                    if 'risk_management' in alert:
                        rm = alert['risk_management']
                        
                        # Position size
                        if 'position_size' in rm and rm['position_size']:
                            ps = rm['position_size']
                            alert_text += f"  Position Size: {ps.get('percentage', 0)}% of capital\n"
                            alert_text += f"  Risk Amount: {ps.get('risk_amount', 0)}% of capital\n"
                        
                        # Stop loss
                        if 'stop_loss' in rm and rm['stop_loss'].get('recommended'):
                            sl = rm['stop_loss']['recommended']
                            alert_text += f"  Stop Loss: ₹{sl['price']} ({sl['distance']}%)\n"
                        
                        # Take profit
                        if 'take_profit' in rm and rm['take_profit'].get('recommended'):
                            tp = rm['take_profit']['recommended']
                            alert_text += f"  Take Profit: ₹{tp['price']} ({tp['distance']}%)\n"
                        
                        # Risk-reward ratio
                        if 'risk_reward_ratio' in rm and rm['risk_reward_ratio']:
                            rr = rm['risk_reward_ratio']
                            alert_text += f"  Risk-Reward: {rr.get('ratio', 0)}:1\n"
                        
                        # Risk tips
                        if 'risk_tips' in rm and rm['risk_tips']:
                            alert_text += f"  Risk Tips: {rm['risk_tips'][0]}\n"
                    
                    alert_text += "\n"
                
                messagebox.showinfo("Signal Alerts", alert_text)
            else:
                messagebox.showinfo("Signal Alerts", "No strong signals found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error getting signal alerts: {e}")
    
    def calculate_position_size(self):
        """Calculate position size based on risk parameters"""
        try:
            account_size = float(self.account_size_entry.get())
            risk_per_trade = float(self.risk_per_trade_entry.get()) / 100
            stop_loss_pct = float(self.stop_loss_pct_entry.get()) / 100
            
            # Calculate position size
            risk_amount = account_size * risk_per_trade
            position_size = risk_amount / stop_loss_pct
            
            # Calculate number of shares (assuming ₹100 per share for example)
            example_share_price = 100
            number_of_shares = int(position_size / example_share_price)
            
            result_text = f"""
Position Size Calculation:
• Account Size: ₹{account_size:,.2f}
• Risk Per Trade: {risk_per_trade * 100}%
• Stop Loss: {stop_loss_pct * 100}%
• Risk Amount: ₹{risk_amount:,.2f}
• Position Size: ₹{position_size:,.2f}
• Number of Shares (₹100/share): {number_of_shares:,}

Risk Management:
• Maximum Loss: ₹{risk_amount:,.2f}
• Position Size %: {(position_size / account_size) * 100:.2f}%
• Risk-Reward Ratio (2:1): ₹{risk_amount * 2:,.2f} profit target
            """
            
            self.position_size_result.config(text=result_text)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating position size: {e}")
    
    def save_risk_settings(self):
        """Save risk management settings"""
        try:
            max_position = float(self.max_position_entry.get()) / 100
            stop_loss = float(self.stop_loss_entry.get()) / 100
            take_profit = float(self.take_profit_entry.get()) / 100
            
            self.bot.set_risk_parameters(max_position, stop_loss, take_profit)
            messagebox.showinfo("Success", "Risk settings saved")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving risk settings: {e}")
    
    def update_all_data(self):
        """Update all data"""
        try:
            def update_thread():
                try:
                    self.bot.update_data()
                    messagebox.showinfo("Success", "Data update completed")
                except Exception as e:
                    messagebox.showerror("Error", f"Error updating data: {e}")
            
            threading.Thread(target=update_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error updating data: {e}")
    
    def cleanup_data(self):
        """Cleanup old data"""
        try:
            self.bot.data_manager.cleanup_old_data()
            messagebox.showinfo("Success", "Data cleanup completed")
        except Exception as e:
            messagebox.showerror("Error", f"Error cleaning up data: {e}")
    
    def generate_report(self):
        """Generate trading report"""
        try:
            report = self.bot.generate_report()
            if report:
                messagebox.showinfo("Success", "Report generated successfully")
            else:
                messagebox.showerror("Error", "Failed to generate report")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report: {e}")
    
    def export_portfolio(self):
        """Export portfolio data"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                portfolio = self.bot.get_portfolio_summary()
                if portfolio:
                    df = pd.DataFrame(portfolio['positions'])
                    df.to_csv(filename, index=False)
                    messagebox.showinfo("Success", f"Portfolio exported to {filename}")
                else:
                    messagebox.showerror("Error", "No portfolio data to export")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting portfolio: {e}")
    
    def run(self):
        """Run the GUI"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"Error running GUI: {e}")
        finally:
            self.bot.cleanup()

if __name__ == "__main__":
    app = StockBotGUI()
    app.run() 