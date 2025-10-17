import json
import pandas as pd
import numpy as np
from datetime import datetime

class SignalAnalyzer:
    def __init__(self, data_file="market_data.json"):
        with open(data_file, 'r') as f:
            self.market_data = json.load(f)
    
    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1:
            return 50.0
        prices = np.array(prices)
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return round(100 - (100 / (1 + rs)), 2)
    
    def calculate_moving_average(self, prices, period=20):
        if len(prices) < period:
            return prices[-1]
        return round(np.mean(prices[-period:]), 2)
    
    def classify_signal(self, data):
        weekly_change = data['weekly_change']
        monthly_change = data['monthly_change']
        prices = data['historical_closes']
        rsi = self.calculate_rsi(prices)
        sma_20 = self.calculate_moving_average(prices, 20)
        current_price = data['current_price']
        
        score = 0
        if weekly_change > 5: score += 3
        elif weekly_change > 2: score += 1
        elif weekly_change < -5: score -= 3
        elif weekly_change < -2: score -= 1
        
        if rsi < 30: score += 2
        elif rsi > 70: score -= 2
        
        if current_price > sma_20: score += 1
        else: score -= 1
        
        if data['volume']['ratio'] > 1.5: score += 1
        
        if score >= 3: signal = "BULLISH"
        elif score <= -3: signal = "BEARISH"
        else: signal = "NEUTRAL"
        
        return {
            "signal": signal,
            "score": score,
            "rsi": rsi,
            "sma_20": sma_20,
            "technical_summary": {
                "price_above_ma": current_price > sma_20,
                "rsi_status": "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral",
                "volume_status": "High" if data['volume']['ratio'] > 1.5 else "Normal"
            }
        }
    
    def detect_projects(self, name, data, signal_info):
        projects = []
        current_price = data['current_price']
        weekly_change = data['weekly_change']
        rsi = signal_info['rsi']
        sma_20 = signal_info['sma_20']
        volume_ratio = data['volume']['ratio']
        resistance = data['price_levels']['high_52w']
        support = data['price_levels']['low_52w']

        if current_price > resistance * 0.98 and volume_ratio > 1.2 and rsi < 70:
            projects.append({"type": "TECHNICAL_BREAKOUT",
                             "description": f"Breaking above 52W high of ₹{resistance:,.2f}",
                             "confidence": "High" if volume_ratio > 1.5 else "Medium"})
        if weekly_change > 5 and current_price > sma_20 and 50 < rsi < 70:
            projects.append({"type": "MOMENTUM_PLAY",
                             "description": f"Strong upward momentum ({weekly_change:.1f}% weekly gain)",
                             "confidence": "High"})
        if rsi < 35 and weekly_change > -10 and current_price > sma_20 * 0.95:
            projects.append({"type": "OVERSOLD_BOUNCE",
                             "description": f"Oversold condition (RSI: {rsi:.1f}), potential recovery",
                             "confidence": "Medium"})
        if 15 < data['price_levels'].get('distance_from_low', 0) < 50 and weekly_change > 0:
            projects.append({"type": "VALUE_OPPORTUNITY",
                             "description": f"Trading {data['price_levels']['distance_from_low']:.1f}% above 52W low with positive momentum",
                             "confidence": "Medium"})
        return projects
    
    def generate_recommendation(self, signal_info, projects, data):
        signal = signal_info['signal']
        score = signal_info['score']
        current_price = data['current_price']
        sma_20 = signal_info['sma_20']

        if signal == "BULLISH" and len(projects) >= 2:
            action = "STRONG BUY"; adjustment = "Increase exposure by 8-10%"
        elif signal == "BULLISH":
            action = "BUY"; adjustment = "Increase exposure by 5%"
        elif signal == "BEARISH" and score <= -4:
            action = "STRONG SELL"; adjustment = "Reduce exposure by 10-15%"
        elif signal == "BEARISH":
            action = "SELL"; adjustment = "Reduce exposure by 5%"
        else:
            action = "HOLD"; adjustment = "Maintain current position"

        if signal == "BULLISH":
            target = round(current_price * 1.10, 2)
            stop_loss = round(max(sma_20, current_price * 0.95), 2)
        elif signal == "BEARISH":
            target = round(current_price * 0.90, 2)
            stop_loss = round(current_price * 1.02, 2)
        else:
            target = current_price
            stop_loss = round(sma_20 * 0.98, 2)
        
        return {
            "action": action,
            "adjustment": adjustment,
            "target_price": target,
            "stop_loss": stop_loss,
            "confidence": "High" if abs(score) >= 4 else "Medium" if abs(score) >= 2 else "Low",
            "rationale": self._generate_rationale(signal, projects, signal_info, data)
        }

    def _generate_rationale(self, signal, projects, signal_info, data):
        parts = []
        if signal == "BULLISH":
            parts.append(f"Weekly gain of {data['weekly_change']:.1f}%")
            if signal_info['rsi'] < 50:
                parts.append(f"RSI at {signal_info['rsi']:.1f} shows room for upside")
            if projects: parts.append(f"{len(projects)} opportunity signals detected")
        elif signal == "BEARISH":
            parts.append(f"Weekly loss of {abs(data['weekly_change']):.1f}%")
            if signal_info['rsi'] > 60:
                parts.append(f"RSI at {signal_info['rsi']:.1f} indicates weakness")
        else:
            parts.append("Mixed technical signals")
        return "; ".join(parts)
    
    def map_to_portfolio_category(self, name, entity_type):
        mapping = {
            "NIFTY_50": "Large Cap Equity", "SENSEX": "Large Cap Equity",
            "BANK_NIFTY": "Banking ETF", "NIFTY_IT": "IT ETF",
            "NIFTY_PHARMA": "Pharma ETF", "NIFTY_AUTO": "Auto ETF",
            "NIFTY_FMCG": "FMCG ETF", "NIFTY_METAL": "Metal ETF", "NIFTY_REALTY": "Real Estate ETF"
        }
        return mapping.get(name, "General Equity")

    def analyze_all(self):
        results = {"analysis_time": datetime.now().isoformat(),
                   "indices": {}, "sectors": {}, "stocks": {}}
        print("=" * 60)
        print("SIGNAL ANALYSIS & PROJECT DETECTION")
        print("=" * 60)

        # Indices
        print("\n Analyzing Indices...")
        for name, data in self.market_data['indices'].items():
            signal_info = self.classify_signal(data)
            projects = self.detect_projects(name, data, signal_info)
            recommendation = self.generate_recommendation(signal_info, projects, data)
            results['indices'][name] = {
                "basic_data": data,
                "portfolio_category": self.map_to_portfolio_category(name, "indices"),
                "signal": signal_info['signal'],
                "technical_indicators": signal_info,
                "projects": projects,
                "recommendation": recommendation
            }
            print(f"✓ {name:15} | {signal_info['signal']:8} | {recommendation['action']:10}")

        # Sectors
        print("\n Analyzing Sectoral Indices...")
        for name, data in self.market_data['sectors'].items():
            signal_info = self.classify_signal(data)
            projects = self.detect_projects(name, data, signal_info)
            recommendation = self.generate_recommendation(signal_info, projects, data)
            results['sectors'][name] = {
                "basic_data": data,
                "portfolio_category": self.map_to_portfolio_category(name, "indices"),
                "signal": signal_info['signal'],
                "technical_indicators": signal_info,
                "projects": projects,
                "recommendation": recommendation
            }
            print(f"✓ {name:15} | {signal_info['signal']:8} | {recommendation['action']:10}")

        # Stocks
        print("\n Analyzing Stocks...")
        for name, data in self.market_data['stocks'].items():
            signal_info = self.classify_signal(data)
            projects = self.detect_projects(name, data, signal_info)
            recommendation = self.generate_recommendation(signal_info, projects, data)
            results['stocks'][name] = {
                "basic_data": data,
                "portfolio_category": "Stock",
                "signal": signal_info['signal'],
                "technical_indicators": signal_info,
                "projects": projects,
                "recommendation": recommendation
            }
            print(f"✓ {name:15} | {signal_info['signal']:8} | {recommendation['action']:10}")

        return results
    
    def save_results(self, results):
        with open('signals.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        rows = []
        for section in ["indices", "sectors", "stocks"]:
            for name, analysis in results[section].items():
                rows.append({
                    "Name": name, "Type": section.capitalize(),
                    "Signal": analysis['signal'],
                    "Action": analysis['recommendation']['action'],
                    "Confidence": analysis['recommendation']['confidence'],
                    "Projects": len(analysis['projects']),
                    "Rationale": analysis['recommendation']['rationale']
                })
        pd.DataFrame(rows).to_csv('signals.csv', index=False)
        print("\nResults saved → signals.json & signals.csv")

if __name__ == "__main__":
    analyzer = SignalAnalyzer()
    results = analyzer.analyze_all()
    analyzer.save_results(results)
