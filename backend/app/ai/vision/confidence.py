from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PredictionCandidate:
    class_index: int
    label: str
    confidence_score: float


def get_top_k_predictions(
    logits,
    class_names: list[str],
    top_k: int = 3,
) -> list[PredictionCandidate]:
    """
    Convert raw logits into sorted top-k prediction candidates.

    Imports torch lazily so the backend can still boot even if torch is not
    installed yet. Only the inference endpoint requires torch/torchvision.
    """
    import torch

    probabilities = torch.softmax(logits, dim=1)
    top_values, top_indices = torch.topk(probabilities, k=top_k, dim=1)

    values = top_values[0].detach().cpu().tolist()
    indices = top_indices[0].detach().cpu().tolist()

    results: list[PredictionCandidate] = []
    for index, value in zip(indices, values, strict=True):
        if 0 <= index < len(class_names):
            label = class_names[index]
        else:
            label = f"class_{index}"

        results.append(
            PredictionCandidate(
                class_index=index,
                label=label,
                confidence_score=round(float(value), 6),
            )
        )

    return results