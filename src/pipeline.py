import argparse
import time

from preprocess import preprocess_data
from train_model import train_model


def run_training_pipeline(
    data_path: str,
    model_path: str = "../models/churn_model.pkl",
    target_col: str = "Churn",
):
    
    start = time.time()

    print("\n╔══════════════════════════════════════════════════════╗")
    print("║      NEXUS · Retention Intelligence Pipeline         ║")
    print("╚══════════════════════════════════════════════════════╝\n")

    model = train_model(
        data_path=data_path,
        model_path=model_path,
        target_col=target_col,
    )

    elapsed = time.time() - start
    print(f"\n  ✓  Pipeline complete in {elapsed:.1f}s")
    print(f"  ✓  Model ready at: {model_path}\n")

    return model


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEXUS Training Pipeline")
    parser.add_argument("--data",   required=True,  help="Path to raw CSV dataset")
    parser.add_argument("--model",  default="../models/churn_model.pkl", help="Output model path")
    parser.add_argument("--target", default="Churn", help="Target column name")
    args = parser.parse_args()

    run_training_pipeline(args.data, args.model, args.target)
