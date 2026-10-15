"""
Inference engine and response generator for the Mental Health Chatbot (Aura).
Loads the trained PyTorch neural network, tokenizes queries, predicts intents,
and returns empathetic contextual responses.
"""

from pathlib import Path
import json
import random
from typing import Optional, Tuple, Dict, Any

import torch

from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

bot_name: str = "Aura"

BASE_DIR = Path(__file__).resolve().parent
INTENTS_FILE = BASE_DIR / "intents.json"
DATA_FILE = BASE_DIR / "data.pth"

CRISIS_KEYWORDS = {
    "kill myself",
    "commit suicide",
    "end my life",
    "want to die",
    "suicidal",
    "self harm",
    "hurt myself",
    "hanging myself",
    "overdose",
}

CRISIS_RESPONSE = (
    "Your life is deeply valuable, and you do not have to carry this alone.\n\n"
    "Please connect with immediate, confidential support right now:\n"
    "• US & Canada: Call or text 988 (Suicide & Crisis Lifeline - 24/7, Free)\n"
    "• UK: Call 111 (NHS) or text SHOUT to 85258\n"
    "• India: Call 1800-599-0019 (KIRAN Mental Health Helpline) or 112\n"
    "• International: Visit https://findahelpline.com for local hotlines\n\n"
    "Please reach out to a trusted loved one, doctor, or emergency counselor immediately."
)

FALLBACK_RESPONSES = [
    "I'm here for you, but I didn't quite catch that. Could you rephrase what you're feeling?",
    "I want to make sure I understand you properly. Could you tell me a little more about that?",
    "I'm listening closely. Could you describe what you're experiencing in another way?",
]


class ChatbotEngine:
    """Manages model loading, intent prediction, and response generation."""

    def __init__(self, data_path: Path = DATA_FILE, intents_path: Path = INTENTS_FILE):
        self.data_path = data_path
        self.intents_path = intents_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model: Optional[NeuralNet] = None
        self.all_words = []
        self.tags = []
        self.intents: Dict[str, Any] = {}
        self.is_loaded = False
        self.load()

    def load(self) -> bool:
        """Load intents and trained PyTorch checkpoint."""
        if not self.intents_path.exists():
            return False

        with open(self.intents_path, "r", encoding="utf-8") as f:
            self.intents = json.load(f)

        if not self.data_path.exists():
            # If checkpoint does not exist yet, trigger auto-training
            try:
                from train import train_model

                print(f"[Aura] '{self.data_path.name}' not found. Auto-training now...")
                train_model(self.intents_path, self.data_path)
            except Exception as e:
                print(f"[Aura] Error during auto-training: {e}")
                return False

        try:
            checkpoint = torch.load(
                str(self.data_path),
                map_location=self.device,
                weights_only=False,
            )
            input_size = checkpoint["input_size"]
            hidden_size = checkpoint["hidden_size"]
            output_size = checkpoint["output_size"]
            self.all_words = checkpoint["all_words"]
            self.tags = checkpoint["tags"]
            model_state = checkpoint["model_state"]

            self.model = NeuralNet(input_size, hidden_size, output_size).to(self.device)
            self.model.load_state_dict(model_state)
            self.model.eval()
            self.is_loaded = True
            return True
        except Exception as e:
            print(f"[Aura] Failed to load checkpoint: {e}")
            self.is_loaded = False
            return False

    def predict_intent(self, sentence: str) -> Tuple[Optional[str], float]:
        """Classify user sentence into intent tag and prediction confidence."""
        if not self.is_loaded or self.model is None:
            return None, 0.0

        tokens = tokenize(sentence)
        if not tokens:
            return None, 0.0

        x = bag_of_words(tokens, self.all_words)
        x = x.reshape(1, x.shape[0])
        x_tensor = torch.from_numpy(x).to(self.device)

        with torch.no_grad():
            output = self.model(x_tensor)
            _, predicted = torch.max(output, dim=1)
            probabilities = torch.softmax(output, dim=1)
            confidence = probabilities[0][predicted.item()].item()
            predicted_tag = self.tags[predicted.item()]

        return predicted_tag, confidence

    def get_response(self, msg: str, threshold: float = 0.70) -> str:
        """
        Generate an empathetic response for the given user message.
        """
        clean_msg = msg.strip().lower()
        if not clean_msg:
            return "I'm here whenever you'd like to talk."

        # Immediate safety check for emergency/crisis terms
        if any(keyword in clean_msg for keyword in CRISIS_KEYWORDS):
            return CRISIS_RESPONSE

        if not self.is_loaded:
            if not self.load():
                return (
                    "I am currently warming up or need to be trained. "
                    "Please run `python train.py` to initialize my knowledge base."
                )

        tag, confidence = self.predict_intent(msg)

        if tag and confidence >= threshold:
            for intent in self.intents.get("intents", []):
                if intent["tag"] == tag:
                    return random.choice(intent["responses"])

        return random.choice(FALLBACK_RESPONSES)


# Global singleton instance for app.py compatibility
_engine = ChatbotEngine()


def get_response(msg: str) -> str:
    """Wrapper function preserving legacy API for GUI integration."""
    return _engine.get_response(msg)


def cli_chat():
    """Terminal interactive chat loop."""
    print("=" * 60)
    print(f"[*] Welcome to {bot_name} - Mental Health Companion (CLI Mode)")
    print("Type 'quit', 'exit', or 'bye' to exit the chat.")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{bot_name}: Take care of yourself! Goodbye.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print(f"{bot_name}: Take care of yourself! Goodbye.")
            break

        reply = get_response(user_input)
        print(f"{bot_name}: {reply}\n")


if __name__ == "__main__":
    cli_chat()