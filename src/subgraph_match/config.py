from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentPaths:
    data_dir: Path = Path('data')
    output_dir: Path = Path('outputs')
    result_dir: Path = Path('results')


@dataclass
class ExperimentConfig:
    paths: ExperimentPaths = field(default_factory=ExperimentPaths)
    enable_filters: bool = True
    max_results: int | None = None
