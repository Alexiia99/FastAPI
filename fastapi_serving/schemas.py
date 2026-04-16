from pydantic import BaseModel, Field

class PredictionRequest(BaseModel):
    Age: int = Field(..., ge=18, le=100)
    BusinessTravel: int = Field(..., ge=0)
    DailyRate: int = Field(..., gt=0)
    Department: int = Field(..., ge=0)
    DistanceFromHome: int = Field(..., ge=0)
    Education: int = Field(..., ge=0)
    EducationField: int = Field(..., ge=0)
    EnvironmentSatisfaction: int = Field(..., ge=0)
    Gender: int = Field(..., ge=0)
    HourlyRate: int = Field(..., gt=0)
    JobInvolvement: int = Field(..., ge=0)
    JobLevel: int = Field(..., ge=0)
    JobRole: int = Field(..., ge=0)
    JobSatisfaction: int = Field(..., ge=0)
    MaritalStatus: int = Field(..., ge=0)
    MonthlyIncome: int = Field(..., gt=0)
    MonthlyRate: int = Field(..., gt=0)
    NumCompaniesWorked: int = Field(..., ge=0)
    OverTime: int = Field(..., ge=0)
    PercentSalaryHike: int = Field(..., ge=0)
    PerformanceRating: int = Field(..., ge=0)
    RelationshipSatisfaction: int = Field(..., ge=0)
    StockOptionLevel: int = Field(..., ge=0)
    TotalWorkingYears: int = Field(..., ge=0)
    TrainingTimesLastYear: int = Field(..., ge=0)
    WorkLifeBalance: int = Field(..., ge=0)
    YearsAtCompany: int = Field(..., ge=0)
    YearsInCurrentRole: int = Field(..., ge=0)
    YearsSinceLastPromotion: int = Field(..., ge=0)
    YearsWithCurrManager: int = Field(..., ge=0)

class PredictionResponse(BaseModel):
    prediction: int
    prediction_label: str