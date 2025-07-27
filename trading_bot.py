import pandas as pd
import numpy as np
import time
import schedule
import threading
from datetime import datetime, timedelta
import logging
from config import Config
from angel_one_api import AngelOneAPI
from technical_indicators import TechnicalIndicators
from data_manager import DataManager

class TradingBot:
    def __init__(self):
        self.config = Config()
        self.api = AngelOneAPI()
        self.indicators = TechnicalIndicators()
        self.data_manager = DataManager()
        self.is_running = False
        self.watchlist = []
        self.risk_management = {
            'max_position_size': self.config.MAX_POSITION_SIZE,
            'stop_loss_pct': self.config.STOP_LOSS_PERCENTAGE,
            'take_profit_pct': self.config.TAKE_PROFIT_PERCENTAGE
        }
        
        # Setup logging
        self.setup_logging()
        

    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/trading_bot.log'),
                    logging.StreamHandler()
                ]
            )
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            print(f"Error setting up logging: {e}")
    

    
    def add_to_watchlist(self, symbol):
        """Add symbol to watchlist"""
        try:
            if symbol not in self.watchlist:
                self.watchlist.append(symbol)
                self.logger.info(f"Added {symbol} to watchlist")
                
                # Download historical data if not available
                existing_data = self.data_manager.get_stock_data(symbol, limit=1)
                if existing_data.empty:
                    self.logger.info(f"Downloading historical data for {symbol}")
                    self.data_manager.download_historical_data(symbol)
                
                return True
            else:
                self.logger.info(f"{symbol} is already in watchlist")
                return False
        except Exception as e:
            self.logger.error(f"Error adding {symbol} to watchlist: {e}")
            return False
    
    def remove_from_watchlist(self, symbol):
        """Remove symbol from watchlist"""
        try:
            if symbol in self.watchlist:
                self.watchlist.remove(symbol)
                self.logger.info(f"Removed {symbol} from watchlist")
                return True
            else:
                self.logger.info(f"{symbol} is not in watchlist")
                return False
        except Exception as e:
            self.logger.error(f"Error removing {symbol} from watchlist: {e}")
            return False
    
    def analyze_symbol(self, symbol):
        """Analyze a single symbol and generate signals"""
        try:
            self.logger.info(f"Analyzing {symbol}...")
            
            # Get latest data
            df = self.data_manager.get_latest_data(symbol, days=365)
            
            if df.empty:
                self.logger.warning(f"No data available for {symbol}")
                return []
            
            # Calculate technical indicators
            df = self.indicators.calculate_all_indicators(df)
            
            # Generate signals
            signals = self.indicators.generate_signals(df)
            
            # Save signals to database
            for signal in signals:
                self.data_manager.save_signal(
                    symbol, 
                    signal['type'], 
                    signal['indicator'], 
                    signal['strength'], 
                    signal['reason']
                )
            
            self.logger.info(f"Generated {len(signals)} signals for {symbol}")
            return signals
            
        except Exception as e:
            self.logger.error(f"Error analyzing {symbol}: {e}")
            return []
    
    def analyze_all_symbols(self):
        """Analyze all symbols in watchlist"""
        try:
            self.logger.info("Starting analysis of all symbols...")
            
            all_signals = {}
            
            for symbol in self.watchlist:
                signals = self.analyze_symbol(symbol)
                if signals:
                    all_signals[symbol] = signals
                
                # Small delay to avoid overwhelming the API
                time.sleep(1)
            
            self.logger.info(f"Analysis complete. Generated signals for {len(all_signals)} symbols")
            return all_signals
            
        except Exception as e:
            self.logger.error(f"Error analyzing all symbols: {e}")
            return {}
    
    def get_signal_details(self, symbol, signal):
        """Get detailed analysis for a signal"""
        try:
            # Get latest data for analysis
            df = self.data_manager.get_latest_data(symbol, days=365)
            
            if df.empty:
                return None
            
            # Calculate all indicators
            df = self.indicators.calculate_all_indicators(df)
            
            # Get current price
            current_price = df['close'].iloc[-1]
            
            # Calculate signal strength and confidence
            signal_strength = self.calculate_signal_strength(df, signal)
            
            # Get support and resistance levels
            support_levels = self.get_support_levels(df)
            resistance_levels = self.get_resistance_levels(df)
            
            # Get Fibonacci levels
            fib_levels = self.get_fibonacci_levels(df)
            
            # Calculate risk management parameters
            risk_management = self.calculate_risk_management(df, signal, current_price, support_levels, resistance_levels)
            
            return {
                'symbol': symbol,
                'signal_type': signal['type'],
                'indicator': signal['indicator'],
                'strength': signal['strength'],
                'reason': signal['reason'],
                'current_price': current_price,
                'signal_strength': signal_strength,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'fibonacci_levels': fib_levels,
                'risk_management': risk_management,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting signal details for {symbol}: {e}")
            return None
    
    def calculate_signal_strength(self, df, signal):
        """Calculate signal strength based on multiple factors"""
        try:
            strength_score = 0
            total_factors = 0
            
            # RSI factor
            if 'rsi' in df.columns and not pd.isna(df['rsi'].iloc[-1]):
                rsi = df['rsi'].iloc[-1]
                if signal['type'] == 'BUY' and rsi < 30:
                    strength_score += 3
                elif signal['type'] == 'SELL' and rsi > 70:
                    strength_score += 3
                total_factors += 1
            
            # MACD factor
            if 'macd' in df.columns and 'macd_signal' in df.columns:
                macd = df['macd'].iloc[-1]
                macd_signal = df['macd_signal'].iloc[-1]
                if signal['type'] == 'BUY' and macd > macd_signal:
                    strength_score += 2
                elif signal['type'] == 'SELL' and macd < macd_signal:
                    strength_score += 2
                total_factors += 1
            
            # Bollinger Bands factor
            if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
                current_price = df['close'].iloc[-1]
                bb_upper = df['bb_upper'].iloc[-1]
                bb_lower = df['bb_lower'].iloc[-1]
                if signal['type'] == 'BUY' and current_price < bb_lower:
                    strength_score += 2
                elif signal['type'] == 'SELL' and current_price > bb_upper:
                    strength_score += 2
                total_factors += 1
            
            # Moving Averages factor
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma_20 = df['sma_20'].iloc[-1]
                sma_50 = df['sma_50'].iloc[-1]
                current_price = df['close'].iloc[-1]
                if signal['type'] == 'BUY' and current_price > sma_20 and sma_20 > sma_50:
                    strength_score += 1
                elif signal['type'] == 'SELL' and current_price < sma_20 and sma_20 < sma_50:
                    strength_score += 1
                total_factors += 1
            
            # Volume factor
            if 'volume' in df.columns:
                avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                current_volume = df['volume'].iloc[-1]
                if current_volume > avg_volume * 1.5:  # 50% above average
                    strength_score += 1
                total_factors += 1
            
            # Calculate final strength
            if total_factors > 0:
                final_strength = (strength_score / total_factors) * 100
                if final_strength >= 80:
                    return "VERY STRONG"
                elif final_strength >= 60:
                    return "STRONG"
                elif final_strength >= 40:
                    return "MEDIUM"
                else:
                    return "WEAK"
            else:
                return "UNKNOWN"
                
        except Exception as e:
            self.logger.error(f"Error calculating signal strength: {e}")
            return "UNKNOWN"
    
    def get_support_levels(self, df):
        """Get support levels for the symbol"""
        try:
            support_levels = []
            
            # Recent lows
            recent_lows = df['low'].tail(20).nsmallest(3)
            for low in recent_lows:
                if not pd.isna(low):
                    support_levels.append(round(low, 2))
            
            # Moving averages as support
            if 'sma_20' in df.columns and not pd.isna(df['sma_20'].iloc[-1]):
                support_levels.append(round(df['sma_20'].iloc[-1], 2))
            if 'sma_50' in df.columns and not pd.isna(df['sma_50'].iloc[-1]):
                support_levels.append(round(df['sma_50'].iloc[-1], 2))
            
            # Fibonacci levels
            if 'fib_618' in df.columns and not pd.isna(df['fib_618'].iloc[-1]):
                support_levels.append(round(df['fib_618'].iloc[-1], 2))
            if 'fib_786' in df.columns and not pd.isna(df['fib_786'].iloc[-1]):
                support_levels.append(round(df['fib_786'].iloc[-1], 2))
            
            return sorted(list(set(support_levels)), reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting support levels: {e}")
            return []
    
    def get_resistance_levels(self, df):
        """Get resistance levels for the symbol"""
        try:
            resistance_levels = []
            
            # Recent highs
            recent_highs = df['high'].tail(20).nlargest(3)
            for high in recent_highs:
                if not pd.isna(high):
                    resistance_levels.append(round(high, 2))
            
            # Moving averages as resistance
            if 'sma_200' in df.columns and not pd.isna(df['sma_200'].iloc[-1]):
                resistance_levels.append(round(df['sma_200'].iloc[-1], 2))
            
            # Fibonacci levels
            if 'fib_236' in df.columns and not pd.isna(df['fib_236'].iloc[-1]):
                resistance_levels.append(round(df['fib_236'].iloc[-1], 2))
            if 'fib_382' in df.columns and not pd.isna(df['fib_382'].iloc[-1]):
                resistance_levels.append(round(df['fib_382'].iloc[-1], 2))
            
            return sorted(list(set(resistance_levels)))
            
        except Exception as e:
            self.logger.error(f"Error getting resistance levels: {e}")
            return []
    
    def get_fibonacci_levels(self, df):
        """Get Fibonacci levels for the symbol"""
        try:
            fib_levels = {}
            
            # Get recent swing high and low
            lookback = 100
            if len(df) >= lookback:
                window = df.tail(lookback)
                swing_high = window['high'].max()
                swing_low = window['low'].min()
                
                # Calculate Fibonacci retracements
                diff = swing_high - swing_low
                fib_levels = {
                    '0%': round(swing_high, 2),
                    '23.6%': round(swing_high - (diff * 0.236), 2),
                    '38.2%': round(swing_high - (diff * 0.382), 2),
                    '50%': round(swing_high - (diff * 0.5), 2),
                    '61.8%': round(swing_high - (diff * 0.618), 2),
                    '78.6%': round(swing_high - (diff * 0.786), 2),
                    '100%': round(swing_low, 2)
                }
            
            return fib_levels
            
        except Exception as e:
            self.logger.error(f"Error getting Fibonacci levels: {e}")
            return {}
    
    def calculate_risk_management(self, df, signal, current_price, support_levels, resistance_levels):
        """Calculate comprehensive risk management parameters"""
        try:
            risk_management = {
                'position_size': {},
                'stop_loss': {},
                'take_profit': {},
                'risk_reward_ratio': {},
                'entry_points': {},
                'exit_strategy': {},
                'risk_tips': [],
                'market_conditions': {},
                'volatility_analysis': {}
            }
            
            # Calculate ATR for volatility
            atr = df['atr'].iloc[-1] if 'atr' in df.columns and not pd.isna(df['atr'].iloc[-1]) else current_price * 0.02
            
            # Position Size Calculation
            risk_management['position_size'] = self.calculate_position_size(current_price, atr, signal['strength'])
            
            # Stop Loss Calculation
            risk_management['stop_loss'] = self.calculate_stop_loss(df, signal, current_price, support_levels, resistance_levels, atr)
            
            # Take Profit Calculation
            risk_management['take_profit'] = self.calculate_take_profit(df, signal, current_price, resistance_levels, support_levels, atr)
            
            # Risk-Reward Ratio
            risk_management['risk_reward_ratio'] = self.calculate_risk_reward_ratio(
                risk_management['stop_loss'], 
                risk_management['take_profit'], 
                current_price
            )
            
            # Entry Points
            risk_management['entry_points'] = self.calculate_entry_points(df, signal, current_price, support_levels, resistance_levels)
            
            # Exit Strategy
            risk_management['exit_strategy'] = self.calculate_exit_strategy(df, signal, current_price, atr)
            
            # Risk Tips
            risk_management['risk_tips'] = self.generate_risk_tips(df, signal, current_price, atr)
            
            # Market Conditions
            risk_management['market_conditions'] = self.analyze_market_conditions(df)
            
            # Volatility Analysis
            risk_management['volatility_analysis'] = self.analyze_volatility(df, atr)
            
            return risk_management
            
        except Exception as e:
            self.logger.error(f"Error calculating risk management: {e}")
            return {}
    
    def calculate_position_size(self, current_price, atr, signal_strength):
        """Calculate recommended position size based on risk"""
        try:
            # Base position size (1% risk per trade)
            base_risk_percentage = 0.01
            
            # Adjust based on signal strength
            strength_multiplier = {
                'WEAK': 0.5,
                'MEDIUM': 1.0,
                'STRONG': 1.5,
                'VERY STRONG': 2.0
            }
            
            multiplier = strength_multiplier.get(signal_strength, 1.0)
            adjusted_risk = base_risk_percentage * multiplier
            
            # Calculate position size based on ATR-based stop loss
            stop_loss_distance = atr * 2  # 2 ATR for stop loss
            risk_per_share = stop_loss_distance
            
            # Position size = Risk amount / Risk per share
            position_size_percentage = adjusted_risk / (stop_loss_distance / current_price)
            
            return {
                'percentage': round(position_size_percentage * 100, 2),
                'risk_amount': round(adjusted_risk * 100, 2),
                'strength_multiplier': multiplier,
                'recommendation': self.get_position_size_recommendation(position_size_percentage, signal_strength)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating position size: {e}")
            return {}
    
    def calculate_stop_loss(self, df, signal, current_price, support_levels, resistance_levels, atr):
        """Calculate optimal stop loss levels"""
        try:
            stop_loss_levels = []
            
            if signal['type'] == 'BUY':
                # For buy signals, stop loss below current price
                
                # ATR-based stop loss
                atr_stop = current_price - (atr * 2)
                stop_loss_levels.append({
                    'type': 'ATR-based',
                    'price': round(atr_stop, 2),
                    'distance': round((current_price - atr_stop) / current_price * 100, 2),
                    'description': 'Based on Average True Range'
                })
                
                # Support-based stop loss
                if support_levels:
                    nearest_support = max([s for s in support_levels if s < current_price], default=None)
                    if nearest_support:
                        stop_loss_levels.append({
                            'type': 'Support-based',
                            'price': round(nearest_support, 2),
                            'distance': round((current_price - nearest_support) / current_price * 100, 2),
                            'description': 'Below nearest support level'
                        })
                
                # Moving average stop loss
                if 'sma_20' in df.columns and not pd.isna(df['sma_20'].iloc[-1]):
                    sma_20 = df['sma_20'].iloc[-1]
                    if sma_20 < current_price:
                        stop_loss_levels.append({
                            'type': 'SMA-20',
                            'price': round(sma_20, 2),
                            'distance': round((current_price - sma_20) / current_price * 100, 2),
                            'description': 'Below 20-day moving average'
                        })
                
            else:  # SELL signal
                # For sell signals, stop loss above current price
                
                # ATR-based stop loss
                atr_stop = current_price + (atr * 2)
                stop_loss_levels.append({
                    'type': 'ATR-based',
                    'price': round(atr_stop, 2),
                    'distance': round((atr_stop - current_price) / current_price * 100, 2),
                    'description': 'Based on Average True Range'
                })
                
                # Resistance-based stop loss
                if resistance_levels:
                    nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
                    if nearest_resistance:
                        stop_loss_levels.append({
                            'type': 'Resistance-based',
                            'price': round(nearest_resistance, 2),
                            'distance': round((nearest_resistance - current_price) / current_price * 100, 2),
                            'description': 'Above nearest resistance level'
                        })
            
            # Sort by distance (closest first)
            stop_loss_levels.sort(key=lambda x: x['distance'])
            
            return {
                'levels': stop_loss_levels,
                'recommended': stop_loss_levels[0] if stop_loss_levels else None,
                'trailing_stop': self.calculate_trailing_stop(df, signal, current_price, atr)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating stop loss: {e}")
            return {}
    
    def calculate_take_profit(self, df, signal, current_price, resistance_levels, support_levels, atr):
        """Calculate take profit levels"""
        try:
            take_profit_levels = []
            
            if signal['type'] == 'BUY':
                # For buy signals, take profit above current price
                
                # ATR-based take profit (3:1 risk-reward)
                atr_tp = current_price + (atr * 6)  # 3x the stop loss distance
                take_profit_levels.append({
                    'type': 'ATR-based (3:1)',
                    'price': round(atr_tp, 2),
                    'distance': round((atr_tp - current_price) / current_price * 100, 2),
                    'description': '3:1 risk-reward ratio'
                })
                
                # Resistance-based take profit
                if resistance_levels:
                    for i, resistance in enumerate(resistance_levels[:3]):  # Top 3 resistance levels
                        if resistance > current_price:
                            take_profit_levels.append({
                                'type': f'Resistance {i+1}',
                                'price': round(resistance, 2),
                                'distance': round((resistance - current_price) / current_price * 100, 2),
                                'description': f'Target resistance level {i+1}'
                            })
                
                # Fibonacci extension
                if 'fib_618' in df.columns and not pd.isna(df['fib_618'].iloc[-1]):
                    fib_tp = df['fib_618'].iloc[-1]
                    if fib_tp > current_price:
                        take_profit_levels.append({
                            'type': 'Fibonacci 61.8%',
                            'price': round(fib_tp, 2),
                            'distance': round((fib_tp - current_price) / current_price * 100, 2),
                            'description': 'Fibonacci 61.8% extension'
                        })
                
            else:  # SELL signal
                # For sell signals, take profit below current price
                
                # ATR-based take profit (3:1 risk-reward)
                atr_tp = current_price - (atr * 6)  # 3x the stop loss distance
                take_profit_levels.append({
                    'type': 'ATR-based (3:1)',
                    'price': round(atr_tp, 2),
                    'distance': round((current_price - atr_tp) / current_price * 100, 2),
                    'description': '3:1 risk-reward ratio'
                })
                
                # Support-based take profit
                if support_levels:
                    for i, support in enumerate(support_levels[:3]):  # Top 3 support levels
                        if support < current_price:
                            take_profit_levels.append({
                                'type': f'Support {i+1}',
                                'price': round(support, 2),
                                'distance': round((current_price - support) / current_price * 100, 2),
                                'description': f'Target support level {i+1}'
                            })
            
            # Sort by distance (closest first)
            take_profit_levels.sort(key=lambda x: x['distance'])
            
            return {
                'levels': take_profit_levels,
                'recommended': take_profit_levels[0] if take_profit_levels else None
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating take profit: {e}")
            return {}
    
    def calculate_risk_reward_ratio(self, stop_loss, take_profit, current_price):
        """Calculate risk-reward ratio"""
        try:
            if not stop_loss.get('recommended') or not take_profit.get('recommended'):
                return {}
            
            stop_price = stop_loss['recommended']['price']
            target_price = take_profit['recommended']['price']
            
            if stop_loss['recommended']['type'].startswith('ATR'):
                # For ATR-based stops, calculate based on ATR
                risk_distance = abs(current_price - stop_price)
                reward_distance = abs(target_price - current_price)
                ratio = reward_distance / risk_distance if risk_distance > 0 else 0
            else:
                # For percentage-based
                risk_pct = stop_loss['recommended']['distance']
                reward_pct = take_profit['recommended']['distance']
                ratio = reward_pct / risk_pct if risk_pct > 0 else 0
            
            return {
                'ratio': round(ratio, 2),
                'risk_percentage': round(stop_loss['recommended']['distance'], 2),
                'reward_percentage': round(take_profit['recommended']['distance'], 2),
                'recommendation': self.get_risk_reward_recommendation(ratio)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating risk-reward ratio: {e}")
            return {}
    
    def calculate_entry_points(self, df, signal, current_price, support_levels, resistance_levels):
        """Calculate optimal entry points"""
        try:
            entry_points = []
            
            if signal['type'] == 'BUY':
                # Current price entry
                entry_points.append({
                    'type': 'Market Entry',
                    'price': current_price,
                    'description': 'Enter at current market price',
                    'priority': 'High' if signal['strength'] == 'VERY STRONG' else 'Medium'
                })
                
                # Pullback entries
                if support_levels:
                    for i, support in enumerate(support_levels[:2]):
                        if support < current_price:
                            entry_points.append({
                                'type': f'Pullback Entry {i+1}',
                                'price': round(support, 2),
                                'description': f'Enter on pullback to support level {i+1}',
                                'priority': 'Medium'
                            })
                
                # Breakout entry
                if resistance_levels:
                    nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
                    if nearest_resistance:
                        entry_points.append({
                            'type': 'Breakout Entry',
                            'price': round(nearest_resistance, 2),
                            'description': 'Enter on breakout above resistance',
                            'priority': 'Low'
                        })
            
            else:  # SELL signal
                # Current price entry
                entry_points.append({
                    'type': 'Market Entry',
                    'price': current_price,
                    'description': 'Enter at current market price',
                    'priority': 'High' if signal['strength'] == 'VERY STRONG' else 'Medium'
                })
                
                # Bounce entries
                if resistance_levels:
                    for i, resistance in enumerate(resistance_levels[:2]):
                        if resistance > current_price:
                            entry_points.append({
                                'type': f'Bounce Entry {i+1}',
                                'price': round(resistance, 2),
                                'description': f'Enter on bounce to resistance level {i+1}',
                                'priority': 'Medium'
                            })
                
                # Breakdown entry
                if support_levels:
                    nearest_support = max([s for s in support_levels if s < current_price], default=None)
                    if nearest_support:
                        entry_points.append({
                            'type': 'Breakdown Entry',
                            'price': round(nearest_support, 2),
                            'description': 'Enter on breakdown below support',
                            'priority': 'Low'
                        })
            
            return entry_points
            
        except Exception as e:
            self.logger.error(f"Error calculating entry points: {e}")
            return []
    
    def calculate_exit_strategy(self, df, signal, current_price, atr):
        """Calculate exit strategy"""
        try:
            exit_strategy = {
                'immediate_exit': [],
                'partial_exit': [],
                'trailing_stop': {},
                'time_based_exit': {}
            }
            
            # Immediate exit conditions
            if signal['type'] == 'BUY':
                exit_strategy['immediate_exit'].extend([
                    'Price breaks below key support level',
                    'RSI moves above 70 (overbought)',
                    'MACD bearish crossover',
                    'Volume spike with price reversal'
                ])
            else:
                exit_strategy['immediate_exit'].extend([
                    'Price breaks above key resistance level',
                    'RSI moves below 30 (oversold)',
                    'MACD bullish crossover',
                    'Volume spike with price reversal'
                ])
            
            # Partial exit strategy
            exit_strategy['partial_exit'] = [
                'Exit 25% at first resistance/support',
                'Exit 25% at 2:1 risk-reward',
                'Exit 25% at 3:1 risk-reward',
                'Hold remaining 25% with trailing stop'
            ]
            
            # Trailing stop
            exit_strategy['trailing_stop'] = {
                'initial_distance': round(atr * 2, 2),
                'adjustment': 'Move stop loss to breakeven after 1:1 risk-reward',
                'final_exit': 'Exit remaining position when trailing stop is hit'
            }
            
            # Time-based exit
            exit_strategy['time_based_exit'] = {
                'short_term': 'Exit within 1-3 days if target not reached',
                'medium_term': 'Exit within 1-2 weeks if target not reached',
                'long_term': 'Exit within 1 month if target not reached'
            }
            
            return exit_strategy
            
        except Exception as e:
            self.logger.error(f"Error calculating exit strategy: {e}")
            return {}
    
    def generate_risk_tips(self, df, signal, current_price, atr):
        """Generate risk management tips"""
        try:
            tips = []
            
            # General risk tips
            tips.append("Never risk more than 1-2% of your capital on a single trade")
            tips.append("Always use stop loss to limit potential losses")
            tips.append("Maintain a minimum 2:1 risk-reward ratio")
            tips.append("Don't chase losses - stick to your trading plan")
            
            # Signal-specific tips
            if signal['strength'] == 'WEAK':
                tips.append("Consider reducing position size due to weak signal")
                tips.append("Wait for stronger confirmation before entering")
                tips.append("Use tighter stop loss due to low confidence")
            
            elif signal['strength'] == 'VERY STRONG':
                tips.append("Signal is very strong - consider normal position size")
                tips.append("Multiple indicators confirming the move")
                tips.append("Higher probability of success")
            
            # Volatility-based tips
            volatility_ratio = atr / current_price
            if volatility_ratio > 0.05:  # High volatility
                tips.append("High volatility detected - use wider stop loss")
                tips.append("Consider reducing position size due to volatility")
            elif volatility_ratio < 0.02:  # Low volatility
                tips.append("Low volatility - tighter stop loss possible")
                tips.append("May need to wait for volatility expansion")
            
            # Market condition tips
            if 'rsi' in df.columns and not pd.isna(df['rsi'].iloc[-1]):
                rsi = df['rsi'].iloc[-1]
                if rsi > 70:
                    tips.append("RSI overbought - be cautious with buy signals")
                elif rsi < 30:
                    tips.append("RSI oversold - be cautious with sell signals")
            
            # Volume tips
            if 'volume' in df.columns:
                avg_volume = df['volume'].rolling(20).mean().iloc[-1]
                current_volume = df['volume'].iloc[-1]
                if current_volume > avg_volume * 2:
                    tips.append("High volume - signal has strong backing")
                elif current_volume < avg_volume * 0.5:
                    tips.append("Low volume - signal may lack conviction")
            
            return tips
            
        except Exception as e:
            self.logger.error(f"Error generating risk tips: {e}")
            return []
    
    def analyze_market_conditions(self, df):
        """Analyze current market conditions"""
        try:
            conditions = {}
            
            # Trend analysis
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                sma_20 = df['sma_20'].iloc[-1]
                sma_50 = df['sma_50'].iloc[-1]
                current_price = df['close'].iloc[-1]
                
                if current_price > sma_20 > sma_50:
                    conditions['trend'] = 'Strong Uptrend'
                elif current_price > sma_20 and sma_20 < sma_50:
                    conditions['trend'] = 'Weak Uptrend'
                elif current_price < sma_20 < sma_50:
                    conditions['trend'] = 'Strong Downtrend'
                elif current_price < sma_20 and sma_20 > sma_50:
                    conditions['trend'] = 'Weak Downtrend'
                else:
                    conditions['trend'] = 'Sideways'
            
            # Volatility analysis
            if 'atr' in df.columns:
                atr = df['atr'].iloc[-1]
                avg_atr = df['atr'].rolling(20).mean().iloc[-1]
                
                if atr > avg_atr * 1.5:
                    conditions['volatility'] = 'High'
                elif atr < avg_atr * 0.5:
                    conditions['volatility'] = 'Low'
                else:
                    conditions['volatility'] = 'Normal'
            
            # Momentum analysis
            if 'rsi' in df.columns:
                rsi = df['rsi'].iloc[-1]
                if rsi > 70:
                    conditions['momentum'] = 'Overbought'
                elif rsi < 30:
                    conditions['momentum'] = 'Oversold'
                else:
                    conditions['momentum'] = 'Neutral'
            
            return conditions
            
        except Exception as e:
            self.logger.error(f"Error analyzing market conditions: {e}")
            return {}
    
    def analyze_volatility(self, df, atr):
        """Analyze volatility patterns"""
        try:
            volatility = {}
            
            # Current volatility
            current_price = df['close'].iloc[-1]
            volatility_ratio = atr / current_price
            volatility['current_ratio'] = round(volatility_ratio * 100, 2)
            
            # Volatility classification
            if volatility_ratio > 0.05:
                volatility['level'] = 'High'
                volatility['implication'] = 'Wider stop losses needed, higher risk'
            elif volatility_ratio < 0.02:
                volatility['level'] = 'Low'
                volatility['implication'] = 'Tighter stop losses possible, lower risk'
            else:
                volatility['level'] = 'Normal'
                volatility['implication'] = 'Standard risk management applies'
            
            # Volatility trend
            if 'atr' in df.columns:
                recent_atr = df['atr'].tail(5).mean()
                if atr > recent_atr * 1.2:
                    volatility['trend'] = 'Increasing'
                elif atr < recent_atr * 0.8:
                    volatility['trend'] = 'Decreasing'
                else:
                    volatility['trend'] = 'Stable'
            
            return volatility
            
        except Exception as e:
            self.logger.error(f"Error analyzing volatility: {e}")
            return {}
    
    def calculate_trailing_stop(self, df, signal, current_price, atr):
        """Calculate trailing stop parameters"""
        try:
            trailing_stop = {}
            
            if signal['type'] == 'BUY':
                trailing_stop['initial_stop'] = round(current_price - (atr * 2), 2)
                trailing_stop['breakeven_level'] = round(current_price + (atr * 2), 2)
                trailing_stop['adjustment_rule'] = 'Move stop to breakeven after 1:1 risk-reward'
            else:
                trailing_stop['initial_stop'] = round(current_price + (atr * 2), 2)
                trailing_stop['breakeven_level'] = round(current_price - (atr * 2), 2)
                trailing_stop['adjustment_rule'] = 'Move stop to breakeven after 1:1 risk-reward'
            
            return trailing_stop
            
        except Exception as e:
            self.logger.error(f"Error calculating trailing stop: {e}")
            return {}
    
    def get_position_size_recommendation(self, position_size, signal_strength):
        """Get position size recommendation"""
        if position_size > 0.05:  # More than 5%
            return "Reduce position size - too large for risk management"
        elif position_size > 0.03:  # 3-5%
            return "Position size is acceptable for strong signals"
        elif position_size > 0.01:  # 1-3%
            return "Good position size for risk management"
        else:
            return "Position size is too small - consider increasing for strong signals"
    
    def get_risk_reward_recommendation(self, ratio):
        """Get risk-reward ratio recommendation"""
        if ratio >= 3:
            return "Excellent risk-reward ratio - highly recommended"
        elif ratio >= 2:
            return "Good risk-reward ratio - recommended"
        elif ratio >= 1.5:
            return "Acceptable risk-reward ratio - proceed with caution"
        else:
            return "Poor risk-reward ratio - avoid this trade"
    
    def generate_signal_report(self, symbol=None):
        """Generate comprehensive signal report"""
        try:
            if symbol:
                symbols_to_analyze = [symbol]
            else:
                symbols_to_analyze = self.watchlist
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'signals': [],
                'summary': {
                    'total_signals': 0,
                    'buy_signals': 0,
                    'sell_signals': 0,
                    'strong_signals': 0,
                    'very_strong_signals': 0
                }
            }
            
            for sym in symbols_to_analyze:
                signals = self.analyze_symbol(sym)
                
                for signal in signals:
                    # Get detailed analysis
                    signal_details = self.get_signal_details(sym, signal)
                    if signal_details:
                        report['signals'].append(signal_details)
                        
                        # Update summary
                        report['summary']['total_signals'] += 1
                        if signal['type'] == 'BUY':
                            report['summary']['buy_signals'] += 1
                        else:
                            report['summary']['sell_signals'] += 1
                        
                        if signal_details['signal_strength'] == 'STRONG':
                            report['summary']['strong_signals'] += 1
                        elif signal_details['signal_strength'] == 'VERY STRONG':
                            report['summary']['very_strong_signals'] += 1
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating signal report: {e}")
            return None
    
    def get_signal_alerts(self, min_strength='MEDIUM'):
        """Get signal alerts based on minimum strength"""
        try:
            alerts = []
            
            for symbol in self.watchlist:
                signals = self.analyze_symbol(symbol)
                
                for signal in signals:
                    signal_details = self.get_signal_details(symbol, signal)
                    if signal_details:
                        # Check if signal meets minimum strength requirement
                        strength_order = ['WEAK', 'MEDIUM', 'STRONG', 'VERY STRONG']
                        signal_strength = signal_details['signal_strength']
                        
                        if strength_order.index(signal_strength) >= strength_order.index(min_strength):
                            alerts.append(signal_details)
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error getting signal alerts: {e}")
            return []
    
    def monitor_signals(self, interval_minutes=5):
        """Monitor signals at regular intervals"""
        try:
            if self.is_running:
                self.logger.warning("Signal monitoring is already running")
                return False
            
            self.is_running = True
            
            def monitor_loop():
                while self.is_running:
                    try:
                        # Get current alerts
                        alerts = self.get_signal_alerts('STRONG')
                        
                        if alerts:
                            self.logger.info(f"Found {len(alerts)} strong signals:")
                            for alert in alerts:
                                self.logger.info(f"  {alert['symbol']} - {alert['signal_type']} ({alert['signal_strength']})")
                        
                        # Wait for next interval
                        time.sleep(interval_minutes * 60)
                        
                    except Exception as e:
                        self.logger.error(f"Error in signal monitoring: {e}")
                        time.sleep(60)  # Wait 1 minute before retrying
            
            monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
            monitor_thread.start()
            
            self.logger.info(f"Signal monitoring started with {interval_minutes} minute intervals")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting signal monitoring: {e}")
            return False
    
    def stop_signal_monitoring(self):
        """Stop signal monitoring"""
        try:
            self.is_running = False
            self.logger.info("Signal monitoring stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping signal monitoring: {e}")
            return False
    
    def get_portfolio_summary(self):
        """Get portfolio summary"""
        try:
            portfolio = self.data_manager.get_portfolio()
            
            if portfolio.empty:
                return {
                    'total_value': 0,
                    'total_pnl': 0,
                    'positions': []
                }
            
            total_value = (portfolio['quantity'] * portfolio['current_price']).sum()
            total_pnl = portfolio['pnl'].sum()
            
            return {
                'total_value': total_value,
                'total_pnl': total_pnl,
                'positions': portfolio.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio summary: {e}")
            return None
    
    def get_recent_signals(self, symbol=None, days=7):
        """Get recent trading signals"""
        try:
            return self.data_manager.get_recent_signals(symbol, days)
        except Exception as e:
            self.logger.error(f"Error getting recent signals: {e}")
            return pd.DataFrame()
    
    def get_trade_history(self, symbol=None, days=30):
        """Get trade history"""
        try:
            return self.data_manager.get_trade_history(symbol, days)
        except Exception as e:
            self.logger.error(f"Error getting trade history: {e}")
            return pd.DataFrame()
    
    def update_data(self, symbol=None):
        """Update market data"""
        try:
            if symbol:
                symbols_to_update = [symbol]
            else:
                symbols_to_update = self.watchlist
            
            for sym in symbols_to_update:
                self.logger.info(f"Updating data for {sym}")
                self.data_manager.update_latest_data(sym)
                time.sleep(1)  # Delay to avoid overwhelming the API
            
            self.logger.info("Data update completed")
            
        except Exception as e:
            self.logger.error(f"Error updating data: {e}")
    
    def set_risk_parameters(self, max_position_size=None, stop_loss_pct=None, take_profit_pct=None):
        """Set risk management parameters"""
        try:
            if max_position_size is not None:
                self.risk_management['max_position_size'] = max_position_size
            
            if stop_loss_pct is not None:
                self.risk_management['stop_loss_pct'] = stop_loss_pct
            
            if take_profit_pct is not None:
                self.risk_management['take_profit_pct'] = take_profit_pct
            
            self.logger.info(f"Risk parameters updated: {self.risk_management}")
            
        except Exception as e:
            self.logger.error(f"Error setting risk parameters: {e}")
    
    def generate_report(self, symbol=None, days=30):
        """Generate trading report"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'portfolio_summary': self.get_portfolio_summary(),
                'recent_signals': self.get_recent_signals(symbol, days).to_dict('records'),
                'trade_history': self.get_trade_history(symbol, days).to_dict('records'),
                'watchlist': self.watchlist,
                'risk_parameters': self.risk_management
            }
            
            # Save report to file
            filename = f"reports/trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            import json
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Report generated: {filename}")
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return None
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.stop_signal_monitoring()
            if self.api.is_connected:
                self.api.logout()
            self.logger.info("Signal analysis bot cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def __del__(self):
        """Destructor"""
        self.cleanup() 