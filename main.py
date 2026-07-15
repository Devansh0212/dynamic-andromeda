import os
import argparse
from engine.data_ingestors import DataIngestor, FredIngestor
from engine.regime_classifier import RegimeClassifier
from knowledge.retriever import Retriever
from insight.memo_generator import MemoGenerator

def main():
    parser = argparse.ArgumentParser(description="Dalio AI Investment Engine")
    parser.add_argument("--date", type=str, help="Simulation date (YYYY-MM-DD)", default=None)
    args = parser.parse_args()
    
    print("--- 1. INGRESTION ---")
    ingestor = FredIngestor()
    # For MVP, we fetch long history
    gdp = ingestor.fetch_series("GDPC1") # Real GDP
    cpi = ingestor.fetch_series("CPIAUCSL") # CPI
    
    print(f"Data Loaded. GDP: {len(gdp)}, CPI: {len(cpi)}")
    
    print("--- 2. CLASSIFICATION ---")
    classifier = RegimeClassifier()
    regime_result = classifier.classify(gdp, cpi, date=args.date)
    print(f"Detected Regime: {regime_result['regime']}")
    print(f"Details: {regime_result['details']}")
    
    print("--- 3. RETRIEVAL ---")
    retriever = Retriever()
    query = f"How to invest during {regime_result['regime']}?"
    principles = retriever.query(query)
    print(f"Retrieved {len(principles)} principles.")
    
    print("--- 4. INSIGHT GENERATION ---")
    gen = MemoGenerator()
    memo = gen.generate_memo(regime_result, principles)
    
    print("\n========== INVESTMENT MEMO ==========")
    print(memo)
    print("=====================================")

if __name__ == "__main__":
    main()
