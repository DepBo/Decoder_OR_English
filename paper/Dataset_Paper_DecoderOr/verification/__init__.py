"""
Verification Package
--------------------
Automated mathematical verification, oracle validation, and mutation testing
for the Decoder-OR logic synthesis benchmark dataset and routing matrices.
"""

from .mutation_test import (
    run_mutation_campaign,
    generate_benchmark_mutations,
    generate_routing_mutations,
    verify_routing_representation,
    MutationResult,
    MutationSummary,
)

__all__ = [
    "run_mutation_campaign",
    "generate_benchmark_mutations",
    "generate_routing_mutations",
    "verify_routing_representation",
    "MutationResult",
    "MutationSummary",
]
