# Intramural Referee Optimization Scheduling System

![Assets\Banner.png](https://github.com/megemann/refscheduling/blob/9085137305b7be9584f4207a59ec50bf2502d8ba/Assets/Banner.png)

## Overview

Intramurals at UMass run year-round, with multiple leagues going at once. For sports like basketball, RecWell hires referees to help create a more professional game environment. As a Program Assistant, part of my job is to recruit, train, develop, and (most importantly) schedule these referees across the season.

**The problem**: scheduling for **150+ teams** over **four nights each week** is incredibly time-consuming. Right now, it mostly means cross-referencing general availability against week-specific conflicts in a giant Excel sheet. **It takes hours, it’s easy to make mistakes, and small changes often mean redoing big chunks of the schedule.**

My goal is to build a scheduling system that cuts through that. The tool automatically generates referee schedules using optimization, supports week-to-week constraint tweaks, exports Excel files for schedules, availability, check-ins, and payroll, and includes simple visualizations of availability and game data to make everything easier to understand. The idea is to make the process faster, more accurate, and more sustainable for future Program Assistants.

The challenges today are:

1. Manual scheduling takes 4+ hours per sport per week
2. Human error leads to conflicts and oversights
3. Last-minute changes cause major rework
4. Payroll tracking is messy
5. Workload distribution isn’t always fair, which hurts morale
6. Scaling up with more leagues or teams just makes all of this worse

Because of that, many PAs just copy last week’s schedule forward. It’s quick, but it keeps the same refs stuck together and means any issues just roll over from week to week with little adjustment.

### My Solution

I built this tool around the real needs of my bosses, past student employees, and the Program Assistant manual. The idea was to make something that slots directly into the existing workflow without adding complexity.

**I prioritized that following features:**
- Excel in/out that matches the files we already use
- Flexible framework to handle week-to-week quirks and exceptions
- **Clear, adjustable objectives** so priorities can shift as needed
- Reusable data so once information is entered, it carries forward
- **Time savings: reduces weekly scheduling from hours to minutes**
- Built-in checks to prevent conflicts and improve fairness across referees

## Features

### Optimization Backend

This project integrates the **Pyomo** framework with **Gurobi** as a backend solver. In order to accelerate time-to-insight, it frames this scheduling problem as an **MILP** (Mixed-Integer Linear Program), which aids in compatability with other linear solvers. The objective is implemented as a mix of the following criteria:
>- Minimizing the difference in hours between officials (Balancing Hours)
>- Awarding higher-effort officials with more hours (Awarding Effort)
>- Minimizing inexperienced officials on difficult games (Matching Game & Ref Experience)
>- Minimizing the number of different independent shift blocks (Scheduling Consecutive Games)
>- Awarding Experienced-Inexperienced Official Pairs (Promoting Teaching)

The objective function allows for a **custom normalized weighting** of objective values to allow for **flexible adjustments** based on customer goals. Additionally, it leverages real consumer feedback as well as direct job documentation when formulating hard and soft constraints for the objective value (i took advice from the PA manual regarding the goals of scheduling). It supports **scaling** to **70+** games with **40+** officials, still offering premium performance in high-throughput situations.

### Streamlit Dashboard

To aid in usage for non-technical student employees, this tool leverages a **streamlit dashboard** that provides visualization, statistics, and custom inputs that follow common practices in recreation. This includes **excel file export / import,** custom constraint assignment and objective weighting, as well as game / official management tools. This abstracts away solver complexity by mapping domain-level inputs (availability, shift requests) to model parameters. It was developed with in conjuction with real consumer feedback and requests. 

## Streamlit (Experimental Preview)

A Streamlit dashboard is in active development to provide a visual interface for uploading data, running optimizations, and inspecting schedules. Revisions are incoming based on user feedback. 

Currently, this feature is **experimental** and subject to significant changes.  
If you’d like to preview it:

```bash
streamlit run dashboard/main.py
```

> Note: functionality is limited and may not reflect the final workflow.
>Detailed documentation will be added once the dashboard stabilizes.
**Demo Video**

You can watch a demonstration of the dashboard in action:

<video src="Assets/9-21-Demo.mp4" controls width="600">
  Your browser does not support the video tag.
</video>

- [▶️ Demo Video (9/21)](Assets/9-21-Demo.mp4)

_Note: If the link does not open in your browser, right-click and select "Open link in new tab" or download the file to view locally._


## Mathematical Formulation

### Decision Variables
<div align="center">

| Symbol           | Type   | Meaning                                                                            |
| ---------------- | ------ | ---------------------------------------------------------------------------------- |
| $x_{i,j,k,l}$    | Binary | $1$ if referee $i$ works on day $j$, hour $k$, game $l$; $0$ otherwise            |
| $a_{i,j,k}$      | Binary | $1$ if referee $i$ is available on day $j$, hour $k$                               |
| $G_{j,k,l}$      | Binary | $1$ if game $l$ is scheduled on day $j$, hour $k$                                  |
| (Auxiliary vars) | Binary | Model shift-block continuity and skill-pairing rules                               |

</div>

### Objective Function
<div align="center">

| Term         | Meaning                                                                 | Weight   |
| ------------ | ----------------------------------------------------------------------- | -------- |
| $e(x)$       | Effort bonus – awards higher-effort officials with more hours           | $w_1$    |
| $b(x)$       | Hour balancing penalty – penalizes deviation from mean hours            | $w_2$    |
| $s(x)$       | Skill penalty – penalizes low average skill compared to game difficulty | $w_3$    |
| $tb(x)$      | Shift-block penalty – penalizes fragmented independent shifts           | $w_4$    |
| $p(x)$       | Pairing bonus – rewards pairing experienced and inexperienced refs       | $w_{5}$  |

<div style="background-color: white; height: 0.5px; width:570px"></div>
</div>

$$
\max \quad obj(x) = w_1 e(x) - w_2 b(x) - w_3 s(x) - w_4 tb(x) + w_{5} p(x)
$$
- _Terms normalized by means for proper weighting_

### Constraints

Hard constraints guarantee feasibility (availability, hour limits, coverage). Soft constraints are encoded as objective penalties/bonuses, allowing the scheduler to trade off fairness, experience, and shift preferences.

#### Hard Constraints

<div align="center">

| Constraint                                                                                                   | Meaning                                                                 |
| ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| $\sum_{g \in G} x_{i,j,k,g} \leq 1$                                                                         | A referee cannot be assigned to more than one game per hour             |
| $\sum_{h \in H}\sum_{g \in G} x_{i,j,h,g} \leq H_{\text{max\_night}}$                                       | No referee can work more than $H_{\text{max\_night}}$ hours in a single night (user-defined) |
| $\sum_{d \in D}\sum_{h \in H}\sum_{g \in G} x_{i,d,h,g} \leq H_{\text{max\_week}}$                          | No referee can be scheduled more than $H_{\text{max\_week}}$ hours per week (user-defined)   |
| $x_{i,j,k,g} \leq a_{i,j,k}$                                                                                | Referees cannot be scheduled outside of their availability              |
| $\text{MIN\_REF}_{g} \leq \sum_{i \in R} x_{i,j,k,g} \leq \text{MAX\_REF}_{g}$                              | Each game $g$ must have between its required minimum and maximum number of referees assigned |
| $x_{i,j,k,g} \leq G_{j,k,g}$                                                                                | Referees can only work games that are actually scheduled                |

</div>

Solver parameters are tuned to balance solution quality with runtime efficiency:

```python
solver.options["OutputFlag"] = 1    # Enable solver progress output
solver.options["TimeLimit"]  = 240  # Maximum runtime (seconds)
solver.options["MIPGap"]     = 0.05 # Allow 5% optimality gap
```

`OutputFlag = 1` → Enables solver log output to track progress in real-time

`TimeLimit = 240` → Limits solver runtime to 4 minutes, ensuring schedules are generated quickly for practical use

`MIPGap = 0.05` → Accepts solutions within 5% of optimality, trading exactness for speed

These settings can be customized depending on the problem size or user preferences (e.g., tighter MIP gap for playoffs, shorter runtime for mid-season batch scheduling).
## Technical Implementation

### Architecture Overview

The system implements a **3-layer architecture** optimized for performance and maintainability:

1. **Data Layer**: Immutable domain models (`Ref`, `Game`) with sparse availability representation and unique identifiers to avoid circular references
2. **Optimization Engine**: Pyomo-based MILP solver with variable pruning (5-20× reduction) and modular objective/constraint building
3. **UI Layer**: Streamlit dashboard with schema validation and Excel integration

### Core Components

**Referee & Game Models**: Frozen dataclasses with sparse availability sets `FrozenSet[Tuple[int, int]]` and normalized skill ratings for optimization compatibility.

**Scheduler Engine**: MILP optimizer using pruned variable sets - only creates `x[ref_id, game_id, day, hour]` where referees are actually available, dramatically reducing problem size.

**Solver Integration**: Multi-backend support (Gurobi → GLPK → CBC) with warm start capabilities, soft coverage constraints, and Irreducible Infeasible Set (IIS) analysis for debugging impossible weeks.

### Key Performance Optimizations

- **Variable Pruning**: Pre-filter decision variables to feasible assignments only
- **Modular Objectives**: Separate building methods for each objective term with internal normalization  
- **Constraint Quality**: Logical variable linking instead of Big-M formulations
- **Warm Starts**: Initialize with manual assignments for faster convergence

### Integration Approach

**Streamlit Adapter**: Thin mapping layer converting Excel uploads → domain objects → optimization parameters, with Pydantic schema validation and domain-specific error messages for non-technical users.

**Results Schema**: Flat assignment records `[{ref_id, game_id, day, hour, court}]` optimized for Excel export and UI display.

**Testing Framework**: Minimal test cases (2 refs × 2 slots × 1 game) with reproducible seeding for constraint validation.

*Full API specifications and implementation details available in [Appendix A: Detailed Technical Implementation](#appendix-a-detailed-technical-implementation)*


## Future Enhancements

The developments planned for the future are:
1. **Reduce Time to Insight:**
   - While 4 minutes is not a bad efficiency bound, **warm starting** and **enhanced variables** would promote faster solution convergence
2. **Enhanced Fusion Integration:**
   - Id like to explore options to integrate this app with functionality of the native game scheduling software to allow for record updates and note considerations
3. **Additional Customizabilty:**
   - Many assumptions are currently be made based on difficulty, referee experience, and domain knowledge. More flexibility for this app would improve future flexibilty.

## License

This project is licensed under the Prosperity Public License 3.0.0.

### Summary

The Prosperity Public License (PPL) 3.0.0 is a source-available license that allows you to use, copy, modify, and distribute the software for non-commercial purposes. Commercial use is only permitted after the specified "Change Date" (if any), or by purchasing a commercial license from the copyright holder.

### Key Terms

- **Non-Commercial Use:** You may use, copy, modify, and distribute this software, in whole or in part, for non-commercial purposes only.
- **Commercial Use:** You may not use this software, in whole or in part, for commercial purposes, except after the Change Date or by purchasing a commercial license.
- **Change Date:** If a Change Date is specified in the license file, the software becomes available for commercial use after that date.
- **No Warranty:** The software is provided "as-is" without warranty of any kind.

For the full license text, see [https://prosperitylicense.com/versions/3.0.0](https://prosperitylicense.com/versions/3.0.0).

### Usage Terms

- You may use, modify, and share this software for non-commercial purposes.
- For commercial use, please contact the copyright holder for licensing.
- You must include a copy of the Prosperity Public License 3.0.0 with any distribution of this software.

If you have questions about what constitutes commercial use, please refer to the official license FAQ: [https://prosperitylicense.com/faq](https://prosperitylicense.com/faq).

---

# Appendix A: Detailed Technical Implementation

## Core Components

### Referee API
```python
from dataclasses import dataclass
from typing import Set, Tuple, Optional, FrozenSet
from pydantic import BaseModel

@dataclass(frozen=True)
class Ref:
    """Immutable referee model with identifiers and ratings"""
    
    # Constructor
    def __init__(self, ref_id: str, name: str, email: str, phone_number: str, 
                 availability: FrozenSet[Tuple[int, int]], experience: int = 3, 
                 effort: int = 3, max_hours_weekly: int = 12, max_hours_nightly: int = 4)
    
    # Immutable Identifiers  
    ref_id: str                              # Unique referee identifier
    name: str                                # Full name
    email: str                               # Contact email
    phone_number: str                        # Contact phone
    
    # Availability Representation (sparse)
    availability: FrozenSet[Tuple[int, int]] # Set of feasible (day, hour) tuples
    
    # Skills & Ratings (1-5 scale)
    experience: int                          # Experience level (1=novice, 5=expert)
    effort: int                              # Effort/reliability rating (1-5)
    max_hours_weekly: int                    # Maximum hours per week
    max_hours_nightly: int                   # Maximum hours per night
    
    # Derived Properties
    def get_experience_normalized(self) -> float:  # 0-1 scale for optimization
    def get_effort_normalized(self) -> float:      # 0-1 scale for optimization
    def is_available(self, day: int, hour: int) -> bool:  # Check specific timeslot
    def get_available_slots(self) -> FrozenSet[Tuple[int, int]]:  # All available slots
```

### Game API
```python
@dataclass(frozen=True)  
class Game:
    """Immutable game model with scheduling constraints"""
    
    # Constructor
    def __init__(self, game_id: str, day: int, hour: int, court: str, 
                 difficulty: str, min_refs: int = 1, max_refs: int = 2,
                 teams: Tuple[str, str] = ("Team A", "Team B"))
    
    # Immutable Identifiers
    game_id: str                             # Unique game identifier  
    day: int                                 # Day index (0=Monday, 6=Sunday)
    hour: int                                # Hour index (0=6:30pm, 1=7:30pm, etc.)
    court: str                               # Court/location identifier
    
    # Game Properties
    difficulty: str                          # Skill level: "recreational", "competitive", "elite"
    min_refs: int                            # Minimum referees required
    max_refs: int                            # Maximum referees allowed
    teams: Tuple[str, str]                   # Participating teams
    
    # Derived Properties  
    def get_timeslot(self) -> Tuple[int, int]:     # Returns (day, hour) tuple
    def get_difficulty_score(self) -> float:       # Normalized difficulty (0-1)
    def requires_experienced_ref(self) -> bool:     # True for competitive+ games
```

### Assignment State (Mutable)
```python
class AssignmentState:
    """Mutable assignment tracking separate from immutable data models"""
    
    def __init__(self, refs: list[Ref], games: list[Game]):
        self.manual_assignments: dict[str, Set[str]] = {}    # ref_id -> {game_ids}
        self.optimized_assignments: dict[str, Set[str]] = {} # ref_id -> {game_ids}
        self.assignment_history: list[dict] = []             # Previous assignments
    
    # Manual Assignment Management
    def add_manual_assignment(self, ref_id: str, game_id: str) -> None:
    def remove_manual_assignment(self, ref_id: str, game_id: str) -> None:
    def get_manual_assignments(self, ref_id: str) -> Set[str]:
    def clear_manual_assignments(self, ref_id: str) -> None:
    
    # Optimized Results
    def set_optimized_assignments(self, assignments: dict[str, Set[str]]) -> None:
    def get_optimized_assignments(self, ref_id: str) -> Set[str]:
    def get_all_assignments(self, ref_id: str) -> Set[str]:  # Manual + optimized
    
    # Conflict Detection
    def validate_assignment(self, ref_id: str, game_id: str) -> bool:
    def get_assignment_conflicts(self) -> list[str]:         # Human-readable conflicts
```

### Scheduler API
```python
class Scheduler:
    """MILP optimization engine with pruned variables and warm starts"""
    
    def __init__(self, refs: list[Ref], games: list[Game], 
                 assignment_state: Optional[AssignmentState] = None,
                 random_seed: int = 42):
        self.refs = refs
        self.games = games  
        self.assignment_state = assignment_state or AssignmentState(refs, games)
        self.random_seed = random_seed                       # Reproducible tie-breaking
        
        # Precomputed indices for variable pruning (5-20x reduction)
        self.feasible_assignments: Set[Tuple[str, str, int, int]] = self._build_feasible_assignments()
        self.ref_availability_map: dict[Tuple[int, int], Set[str]] = self._build_ref_availability()
        self.game_timeslot_map: dict[Tuple[int, int], Set[str]] = self._build_game_timeslots()
    
    # Configuration
    def set_objective_weights(self, weights: ObjectiveWeights) -> None:
    def set_constraint_limits(self, limits: ConstraintLimits) -> None:
    def set_warm_start(self, assignments: dict[str, Set[str]]) -> None:  # Manual assignments
    
    # Optimization
    def optimize(self) -> SchedulingResults:                 # Returns structured results
    def compute_infeasibility_analysis(self) -> InfeasibilityReport:  # IIS when infeasible
    
    # Variable Pruning (Performance Critical)
    def _build_feasible_assignments(self) -> Set[Tuple[str, str, int, int]]:
        """Only include (ref_id, game_id, day, hour) where ref is available"""
    
    def _build_ref_availability(self) -> dict[Tuple[int, int], Set[str]]:
        """Precompute available refs per timeslot for constraint generation"""
    
    def _build_game_timeslots(self) -> dict[Tuple[int, int], Set[str]]:
        """Precompute games per timeslot for constraint generation"""

# Configuration Models
@dataclass
class ObjectiveWeights:
    effort_bonus: float = 0.2                # w1: Reward high-effort refs
    hour_balance: float = 0.3                # w2: Minimize hour deviation  
    skill_matching: float = 0.25             # w3: Match ref skill to game difficulty
    shift_consolidation: float = 0.15        # w4: Prefer consecutive games
    pairing_bonus: float = 0.1               # w5: Pair experienced + inexperienced

@dataclass  
class ConstraintLimits:
    max_hours_weekly: int = 12               # Default weekly hour limit
    max_hours_nightly: int = 4               # Default nightly hour limit  
    coverage_penalty: float = 1000.0        # Soft coverage violation penalty
    enable_soft_coverage: bool = True        # Allow understaffed games with penalty
```

## Solver Integration
```python
import pyomo.environ as pyo
from typing import Dict, List, Set, Tuple, Optional, Union
from enum import Enum

class SolverInterface:
    """MILP solver integration with Pyomo framework and variable pruning"""
    
    def __init__(self, solver_name: str = "gurobi", random_seed: int = 42):
        self.solver_name = solver_name
        self.random_seed = random_seed
        self.model: Optional[pyo.ConcreteModel] = None
        
    # Solver Management
    def set_solver(self, solver_name: str) -> None:
    def check_solver_availability(self) -> bool:
    def get_available_solvers(self) -> List[str]:
    
    # Model Building with Variable Pruning
    def create_model(self, feasible_assignments: Set[Tuple[str, str, int, int]], 
                     ref_availability: Dict[Tuple[int, int], Set[str]],
                     game_timeslots: Dict[Tuple[int, int], Set[str]]) -> pyo.ConcreteModel:
        """Build model with pruned variables - only feasible (ref,game,day,hour) tuples"""
    
    def build_decision_variables(self, model: pyo.ConcreteModel) -> None:
        """x[ref_id, game_id, day, hour] binary variables (pruned set only)"""
    
    def build_auxiliary_variables(self, model: pyo.ConcreteModel) -> None:
        """Slack variables for soft coverage constraints"""
    
    # Constraint Building (Modular)
    def add_availability_constraints(self, model: pyo.ConcreteModel) -> None:
        """x[i,g,d,h] <= a[i,d,h] - refs only work when available"""
    
    def add_coverage_constraints(self, model: pyo.ConcreteModel, 
                                enable_soft: bool = True) -> None:
        """Game coverage with optional slack variables for infeasible weeks"""
    
    def add_hour_limit_constraints(self, model: pyo.ConcreteModel, 
                                  limits: ConstraintLimits) -> None:
        """Weekly and nightly hour limits per referee"""
    
    def add_conflict_constraints(self, model: pyo.ConcreteModel) -> None:
        """Referee cannot work multiple games simultaneously"""
    
    # Objective Function (Modular Components)
    def build_objective(self, model: pyo.ConcreteModel, weights: ObjectiveWeights) -> None:
        """Weighted sum of normalized objective terms"""
    
    def build_effort_bonus(self, model: pyo.ConcreteModel) -> pyo.Expression:
        """Reward high-effort refs with more hours (normalized)"""
    
    def build_hour_balance(self, model: pyo.ConcreteModel) -> pyo.Expression:
        """Minimize deviation from mean hours across refs (normalized)"""
    
    def build_skill_matching(self, model: pyo.ConcreteModel) -> pyo.Expression:
        """Penalize low avg skill vs game difficulty (normalized)"""
    
    def build_shift_consolidation(self, model: pyo.ConcreteModel) -> pyo.Expression:
        """Minimize fragmented independent shift blocks (normalized)"""
    
    def build_pairing_bonus(self, model: pyo.ConcreteModel) -> pyo.Expression:
        """Reward experienced-inexperienced ref pairings (normalized)"""
    
    # Warm Start Support
    def set_warm_start(self, model: pyo.ConcreteModel, 
                      manual_assignments: Dict[str, Set[str]]) -> None:
        """Initialize x[i,g,d,h].value = 1 for manual assignments"""
    
    # Solver Configuration
    def configure_solver_options(self, time_limit: int = 240, mip_gap: float = 0.05,
                               output_flag: bool = True, **kwargs) -> None:
    
    # Optimization
    def solve(self, model: pyo.ConcreteModel) -> 'SchedulingResults':
    def get_termination_condition(self) -> str:
    def extract_solution(self, model: pyo.ConcreteModel) -> List[Dict[str, Union[str, int]]]:
        """Return flat assignment records: [{ref_id, game_id, day, hour, court}]"""
    
    # Infeasibility Analysis
    def compute_iis(self, model: pyo.ConcreteModel) -> 'InfeasibilityReport':
        """Compute Irreducible Infeasible Set when no solution exists"""

# Results Schema
@dataclass
class SchedulingResults:
    """Structured optimization results with metadata"""
    
    assignments: List[Dict[str, Union[str, int]]]    # Flat records for Excel/UI
    solve_metadata: 'SolveMetadata'
    constraint_violations: List[str]                 # Human-readable warnings
    objective_breakdown: Dict[str, float]            # Individual term values
    
    def is_optimal(self) -> bool:
    def is_feasible(self) -> bool:
    def get_assignments_by_ref(self) -> Dict[str, List[str]]:  # ref_id -> [game_ids]
    def get_assignments_by_game(self) -> Dict[str, List[str]]: # game_id -> [ref_ids]
    def export_to_excel_format(self) -> List[Dict[str, str]]:  # Streamlit-ready data

@dataclass  
class SolveMetadata:
    """Solver performance and quality metrics"""
    
    status: str                                      # "optimal", "feasible", "infeasible", "timeout"
    objective_value: float
    solve_time: float                                # Seconds
    mip_gap: float                                   # Final optimality gap
    nodes_explored: Optional[int] = None             # B&B nodes (if available)
    iterations: Optional[int] = None                 # Solver iterations
    variables_count: int = 0                         # Total decision variables
    constraints_count: int = 0                       # Total constraints
    
@dataclass
class InfeasibilityReport:
    """Analysis of why no feasible solution exists"""
    
    conflicting_constraints: List[str]               # IIS constraint names
    problematic_timeslots: List[Tuple[int, int]]     # Under-covered (day,hour)
    overdemanded_refs: List[str]                     # Refs with too many manual assignments
    suggested_fixes: List[str]                       # Human-readable recommendations
```

## Variable Pruning Strategy
```python
# Only create x[i,g,d,h] variables where:
# 1. Referee i is available at (d,h): (d,h) ∈ availability[i] 
# 2. Game g occurs at timeslot (d,h): game.day == d and game.hour == h
# 3. Reduces binary variables by 5-20× in typical instances

feasible_vars = {(ref.ref_id, game.game_id, game.day, game.hour) 
                 for ref in refs for game in games 
                 if (game.day, game.hour) in ref.availability}
```

## Constraint Quality Improvements
- **No Big-M**: Use logical variable linking `x[i,g,d,h] <= G[d,h,g]` instead of artificial constants
- **Soft Coverage**: Optional slack variables `s[g] >= min_refs[g] - Σ x[i,g,d,h]` with penalty `M * s[g]`
- **Separate Limits**: Weekly AND nightly hour constraints for realistic workload control

## Testing & Reproducibility
```python
class SchedulerTesting:
    """Unit testing framework for MILP constraint validation"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed              # Deterministic tie-breaking
        
    # Minimal Test Cases (Performance)
    def test_basic_feasibility(self) -> None:
        """2 refs × 2 timeslots × 1 game - verify basic assignment"""
        
    def test_availability_constraints(self) -> None:
        """Ensure refs only assigned when available"""
        
    def test_hour_limits(self) -> None:
        """Verify weekly/nightly hour constraints respected"""
        
    def test_coverage_requirements(self) -> None:
        """Games get minimum required referees"""
        
    def test_conflict_prevention(self) -> None:
        """No ref assigned to multiple simultaneous games"""
        
    # Reproducibility Tests
    def test_deterministic_results(self) -> None:
        """Same input → same output with fixed random seed"""
        
    def test_warm_start_consistency(self) -> None:
        """Manual assignments preserved in final solution"""
        
    # Edge Cases
    def test_infeasible_scenarios(self) -> None:
        """Properly detect and report impossible weeks"""
        
    def test_minimal_availability(self) -> None:
        """Handle weeks with very limited ref availability"""

# Reproducible Configuration
@dataclass
class ReproducibleConfig:
    random_seed: int = 42                           # All stochastic operations
    tie_break_method: str = "lexicographic"         # Consistent variable ordering
    solver_threads: int = 1                         # Single-threaded for consistency
```

## Streamlit Integration
```python
from pydantic import BaseModel, validator
from typing import Dict, Any

class StreamlitAdapter:
    """Thin UI layer mapping domain inputs to optimization parameters"""
    
    def __init__(self):
        self.schema_validator = SchedulingInputSchema()
        
    # Input Validation & Schema Mapping
    def validate_referee_upload(self, excel_data: pd.DataFrame) -> List[Ref]:
        """Convert Excel availability → Ref objects with validation"""
        
    def validate_game_upload(self, excel_data: pd.DataFrame) -> List[Game]:
        """Convert Excel game data → Game objects with validation"""
        
    def map_ui_weights_to_objective(self, ui_sliders: Dict[str, float]) -> ObjectiveWeights:
        """Map Streamlit sliders → normalized objective weights"""
        
    def map_ui_limits_to_constraints(self, ui_inputs: Dict[str, int]) -> ConstraintLimits:
        """Map UI form inputs → constraint parameter objects"""
    
    # Results Processing for UI
    def format_results_for_display(self, results: SchedulingResults) -> Dict[str, Any]:
        """Convert optimization results → Streamlit-friendly display format"""
        
    def generate_excel_export(self, results: SchedulingResults) -> bytes:
        """Create downloadable Excel file from scheduling results"""
        
    def create_conflict_report(self, violations: List[str]) -> str:
        """Human-readable constraint violation summary"""
        
    # Error Handling for Non-Technical Users
    def handle_infeasible_solution(self, report: InfeasibilityReport) -> Dict[str, str]:
        """Convert technical IIS analysis → actionable user guidance"""

# Input Schema Validation (Pydantic)
class SchedulingInputSchema(BaseModel):
    """Validate all user inputs before optimization"""
    
    refs: List[Dict[str, Any]]
    games: List[Dict[str, Any]]  
    objective_weights: Dict[str, float]
    constraint_limits: Dict[str, int]
    
    @validator('objective_weights')
    def weights_sum_to_one(cls, v):
        if abs(sum(v.values()) - 1.0) > 0.01:
            raise ValueError("Objective weights must sum to 1.0")
        return v
        
    @validator('refs')
    def validate_availability_format(cls, v):
        # Ensure availability data is properly formatted
        for ref in v:
            if 'availability' not in ref:
                raise ValueError(f"Referee {ref.get('name', 'Unknown')} missing availability data")
        return v

# Domain-Level Error Messages
ERROR_MESSAGES = {
    'infeasible': "Not enough available referees for the scheduled games. Consider: reducing game count, recruiting more refs, or relaxing hour limits.",
    'timeout': "Optimization taking longer than expected. Consider: simplifying constraints or reducing problem size.",
    'no_solver': "Optimization engine not available. Please install Gurobi or ensure GLPK is configured properly."
}
```

## Solver Backend Support
- **Primary**: Gurobi (commercial, high-performance)
- **Fallback**: GLPK (open-source, GNU Linear Programming Kit)  
- **Alternative**: CBC (COIN-OR Branch and Cut)

## Termination Handling
```python
# Robust termination condition processing
termination_map = {
    "optimal": "Optimal solution found",
    "feasible": "Good solution found within time limit", 
    "infeasible": "No valid assignment exists with current constraints",
    "unbounded": "Problem formulation error - objective unbounded",
    "timeout": "Time limit exceeded - returning best solution found"
}
```
