from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Quantity(BaseModel):
    value: float
    unit: str

class InputChemical(BaseModel):
    name: str
    role: Literal["substrate","reagent","catalyst","solvent","base","acid","oxidant","reductant","reactant","other"] = "reagent"
    amount: Optional[Quantity] = None
    equivalents: Optional[float] = None
    smiles: Optional[str] = None

class Conditions(BaseModel):
    temperature: Optional[Quantity] = None
    time: Optional[Quantity] = None
    atmosphere: Optional[str] = None  # e.g. N2, Ar
    solvents: List[str] = Field(default_factory=list)
    ph: Optional[float] = None

class Workup(BaseModel):
    steps: List[str] = Field(default_factory=list)

class Outcome(BaseModel):
    yield_: Optional[Quantity] = Field(default=None, alias="yield")
    product_name: Optional[str] = None
    product_smiles: Optional[str] = None

class Reaction(BaseModel):
    title: Optional[str] = None
    inputs: List[InputChemical]
    conditions: Conditions
    workup: Workup
    outcome: Outcome
    notes: List[str] = Field(default_factory=list)

class ReactionSet(BaseModel):
    document_title: Optional[str] = None
    section_title: Optional[str] = None
    source_url: Optional[str] = None
    reactions: List[Reaction]
