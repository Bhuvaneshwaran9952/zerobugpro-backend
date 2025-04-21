from sqlalchemy import create_engine, Boolean, Column, Integer, String, DECIMAL, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.types import JSON
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging
from datetime import date
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from fastapi import  HTTPException, Depends
from sqlalchemy.orm import Session

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost/SampleDB")

# Initialize FastAPI app
app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def format_pay_date():
    pay_date = datetime.now()  # This is a datetime object
    pay_date_str = pay_date.strftime("%Y-%m-%d")  # Convert to string
    return {"pay_date": pay_date_str}


# ========== MODELS ==========
class User(Base):   
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, index=True)
    course = Column(String, index=True)
    selectCity = Column(String, index=True)
    answer = Column(String, nullable=True) 
    dateTime = Column(String, nullable=False)  
    payment = Column(String, index=True)
    address = Column(String, index=True)
    status = Column(String, index=True)
    certificate = Column(String, index=True)
    is_active = Column(Boolean, default=True)

class Trainer(Base):   
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    contact = Column(String, index=True)
    subject = Column(JSON, nullable=False)  
    address = Column(String, index=True)
    is_active = Column(Boolean, default=True)

class View(Base):   
    __tablename__ = "views"  
    id = Column(Integer, primary_key=True, index=True)
    trainerName = Column(String, index=True)
    subject = Column(JSON, nullable=False) 
    assignedStudents = Column(JSON, nullable=False) 
    batchTime = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class PaymentDetails(Base):
    __tablename__ = "payment_details"
    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, index=True, nullable=False)
    payment_method = Column(String, nullable=False)
    pay_amount = Column(DECIMAL(10,2), nullable=False, default=0.00)
    pending_payment = Column(DECIMAL(10,2), nullable=False, default=0.00)
    pay_date = Column(Date, nullable=False)   
    due_date = Column(Date, nullable=False)

class TrainerPayment(Base):
    __tablename__ = "trainer_payment"

    id = Column(Integer, primary_key=True, index=True)
    trainer_name = Column(String, index=True, nullable=False)
    payment_method = Column(String, nullable=False)
    pay_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    pending_payment = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    pay_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    student_name = Column(String, nullable=False)  
    pay_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    refund_amount = Column(DECIMAL(10, 2), nullable=False, default=0.00)

# Create database tables
Base.metadata.create_all(bind=engine)

# ========== SCHEMAS ==========
class UserBase(BaseModel):
    name: str
    email: str
    phone: str
    course: str
    selectCity: Optional[str]
    dateTime: Optional[str] = datetime.utcnow().isoformat() 
    payment: str
    address: str
    status: Optional[str] = None 
    certificate: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    class Config:
        orm_mode = True

class TrainerBase(BaseModel):
    name: str
    email: str
    contact: str
    subject: list
    address: str
    is_active: bool = True

class TrainerCreate(TrainerBase):
    pass

class TrainerResponse(TrainerBase):
    id: int
    class Config:
        orm_mode = True

class ViewBase(BaseModel):
    trainerName: str
    subject: list
    assignedStudents: list
    batchTime: str
    is_active: bool = True

class ViewCreate(ViewBase):
    pass

class ViewResponse(ViewBase):
    id: int
    class Config:
        orm_mode = True

class PaymentBase(BaseModel):
    student_name: str
    payment_method: str
    pay_amount: float
    pending_payment: float
    pay_date: str 
    due_date: date

class Config:
    orm_mode = True

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int
    class Config:
        orm_mode = True

class TrainerPaymentBase(BaseModel):
    trainer_name: str
    payment_method: str
    pay_amount: float
    pending_payment: float
    pay_date: date
    due_date: date

    class Config:
        orm_mode = True


class TrainerPaymentCreate(TrainerPaymentBase):
    pass


class TrainerPaymentResponse(TrainerPaymentBase):
    id: int


class RefundBase(BaseModel):
    student_name: str
    pay_amount: float
    refund_amount: float

class RefundCreate(RefundBase):
    pass

class RefundUpdate(RefundBase):
    pass

class RefundResponse(RefundBase):
    id: int

    class Config:
        orm_mode = True



# ========== USER CRUD ==========
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # if not user.dateTime:  # Assign default value if None
            # user.dateTime = datetime.utcnow().isoformat()

        logging.info(f"Processed data: {user.dict()}")

        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")



@app.get("/users", response_model=List[UserResponse])
def read_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserBase, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    for key, value in user.dict().items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": f"User with ID {user_id} deleted successfully"}


# ========== TRAINER CRUD ==========
@app.post("/trainer", response_model=TrainerResponse)
def create_trainer(trainer: TrainerCreate, db: Session = Depends(get_db)):
    db_trainer = Trainer(**trainer.dict())
    db.add(db_trainer)
    db.commit()
    db.refresh(db_trainer)
    return db_trainer

@app.get("/trainer", response_model=List[TrainerResponse])
def read_trainers(db: Session = Depends(get_db)):
    return db.query(Trainer).all()

@app.get("/trainer/{trainer_id}", response_model=TrainerResponse)
def read_trainer(trainer_id: int, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    return db_trainer

@app.put("/trainer/{trainer_id}", response_model=TrainerResponse)
def update_trainer(trainer_id: int, trainer: TrainerBase, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    
    for key, value in trainer.dict().items():
        setattr(db_trainer, key, value)
    
    db.commit()
    db.refresh(db_trainer)
    return db_trainer


@app.delete("/trainer/{trainer_id}", response_model=dict)
def delete_trainer(trainer_id: int, db: Session = Depends(get_db)):
    db_trainer = db.query(Trainer).filter(Trainer.id == trainer_id).first()
    if not db_trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")
    db.delete(db_trainer)
    db.commit()
    return {"message": f"Trainer with ID {trainer_id} deleted successfully"}


# ========== VIEW CRUD ==========
@app.post("/view", response_model=ViewResponse)
def create_view(view: ViewCreate, db: Session = Depends(get_db)):
    db_view = View(**view.dict())
    db.add(db_view)
    db.commit()
    db.refresh(db_view)
    return db_view

@app.get("/view", response_model=List[ViewResponse])
def read_views(db: Session = Depends(get_db)):
    print("Fetching all views")
    views = db.query(View).all()
    return views

@app.get("/view/{view_id}", response_model=ViewResponse)
def read_view(view_id: int, db: Session = Depends(get_db)):
    print(f"Fetching view with ID {view_id}")
    db_view = db.query(View).filter(View.id == view_id).first()
    if not db_view:
        raise HTTPException(status_code=404, detail="View not found")
    return db_view

# @app.get("/view/{trainer_id}")
# def get_assignments_for_trainer(trainer_id: int):
#     return db.query(Assignment).filter(Assignment.trainer_id == trainer_id).all()


@app.put("/view/{view_id}", response_model=ViewResponse)
def update_view(view_id: int, view: ViewBase, db: Session = Depends(get_db)):
    print(f"Updating view with ID {view_id}")
    db_view = db.query(View).filter(View.id == view_id).first()
    if not db_view:
        raise HTTPException(status_code=404, detail="View not found")
    
    for key, value in view.dict().items():
        setattr(db_view, key, value)
    
    db.commit()
    db.refresh(db_view)
    return db_view

@app.delete("/view/{view_id}", response_model=dict)
def delete_view(view_id: int, db: Session = Depends(get_db)):
    print(f"Deleting view with ID {view_id}")
    db_view = db.query(View).filter(View.id == view_id).first()
    if not db_view:
        raise HTTPException(status_code=404, detail="View not found")
    db.delete(db_view)
    db.commit()
    return {"message": f"View with ID {view_id} deleted successfully"}

# ========== PAYMENT CRUD ==========
@app.post("/payment")
def create_payment(payment_data: PaymentBase, db: Session = Depends(get_db)):
    new_payment = PaymentDetails(**payment_data.dict())

    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    # Convert `pay_date` and `due_date` to string before returning
    return {
        "id": new_payment.id,
        "student_name": new_payment.student_name,
        "payment_method": new_payment.payment_method,
        "pay_amount": float(new_payment.pay_amount),  # Convert Decimal to float
        "pending_payment": float(new_payment.pending_payment),  # Convert Decimal to float
        "pay_date": new_payment.pay_date.strftime("%Y-%m-%d"),  # Convert to string
        "due_date": new_payment.due_date.strftime("%Y-%m-%d")  # Convert to string
    }

@app.get("/payment", response_model=List[PaymentResponse])
def read_payments(db: Session = Depends(get_db)):
    payments = db.query(PaymentDetails).all()
    return [
        {
            "id": payment.id,
            "student_name": payment.student_name,
            "payment_method": payment.payment_method,
            "pay_amount": payment.pay_amount,
            "pending_payment": payment.pending_payment,
            "pay_date": payment.pay_date.isoformat() if payment.pay_date else None,
            "due_date": payment.due_date.isoformat() if payment.due_date else None
        }
        for payment in payments
    ]



@app.get("/payment/{payment_id}", response_model=PaymentResponse)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(PaymentDetails).filter(PaymentDetails.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Convert pay_date to string before returning
    return {
        "id": db_payment.id,
        "student_name": db_payment.student_name,
        "payment_method": db_payment.payment_method,
        "pay_amount": db_payment.pay_amount,
        "pending_payment": db_payment.pending_payment,
        "pay_date": db_payment.pay_date.isoformat() if db_payment.pay_date else None,
        "due_date": db_payment.due_date.isoformat() if db_payment.due_date else None
    }



from datetime import datetime

@app.put("/payment/{payment_id}")
def update_payment(payment_id: int, updated_data: PaymentBase, db: Session = Depends(get_db)):
    payment = db.query(PaymentDetails).filter(PaymentDetails.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    for key, value in updated_data.dict().items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)

    # Convert `pay_date` to string before returning response
    return {
        "id": payment.id,
        "student_name": payment.student_name,
        "payment_method": payment.payment_method,
        "pay_amount": float(payment.pay_amount),  # Convert Decimal to float
        "pending_payment": float(payment.pending_payment),  # Convert Decimal to float
        "pay_date": payment.pay_date.strftime("%Y-%m-%d"),  # Convert date to string
        "due_date": payment.due_date.strftime("%Y-%m-%d")  # Convert date to string
    }



@app.delete("/payment/{payment_id}", response_model=dict)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(PaymentDetails).filter(PaymentDetails.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    db.delete(db_payment)
    db.commit()
    return {"message": f"Payment with ID {payment_id} deleted successfully"}

# ========== TRAINER PAYMENT CRUD OPERATIONS ==========

# Create a new trainer payment
@app.post("/trainerpayment", response_model=TrainerPaymentResponse)
def create_trainer_payment(payment: TrainerPaymentCreate, db: Session = Depends(get_db)):
    new_payment = TrainerPayment(**payment.dict())
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)

    return {
        "id": new_payment.id,
        "trainer_name": new_payment.trainer_name,
        "payment_method": new_payment.payment_method,
        "pay_amount": float(new_payment.pay_amount),
        "pending_payment": float(new_payment.pending_payment),
        "pay_date": new_payment.pay_date.strftime("%Y-%m-%d"),
        "due_date": new_payment.due_date.strftime("%Y-%m-%d"),
    }


# Get all trainer payments
@app.get("/trainerpayment", response_model=List[TrainerPaymentResponse])
def read_trainer_payments(db: Session = Depends(get_db)):
    payments = db.query(TrainerPayment).all()
    return [
        {
            "id": payment.id,
            "trainer_name": payment.trainer_name,
            "payment_method": payment.payment_method,
            "pay_amount": float(payment.pay_amount),
            "pending_payment": float(payment.pending_payment),
            "pay_date": payment.pay_date.strftime("%Y-%m-%d"),
            "due_date": payment.due_date.strftime("%Y-%m-%d"),
        }
        for payment in payments
    ]


# Get a single trainer payment by ID
@app.get("/trainerpayment/{payment_id}", response_model=TrainerPaymentResponse)
def read_trainer_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(TrainerPayment).filter(TrainerPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Trainer payment not found")

    return {
        "id": db_payment.id,
        "trainer_name": db_payment.trainer_name,
        "payment_method": db_payment.payment_method,
        "pay_amount": float(db_payment.pay_amount),
        "pending_payment": float(db_payment.pending_payment),
        "pay_date": db_payment.pay_date.strftime("%Y-%m-%d"),
        "due_date": db_payment.due_date.strftime("%Y-%m-%d"),
    }

@app.get("/trainerpayment/{id}")
async def get_payment(id: int):
    return {"message": "Trainer Payment Found", "id": id}


# Update a trainer payment
@app.put("/trainerpayment/{payment_id}", response_model=TrainerPaymentResponse)
def update_trainer_payment(payment_id: int, updated_data: TrainerPaymentBase, db: Session = Depends(get_db)):
    payment = db.query(TrainerPayment).filter(TrainerPayment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Trainer payment not found")

    for key, value in updated_data.dict().items():
        setattr(payment, key, value)

    db.commit()
    db.refresh(payment)

    return {
        "id": payment.id,
        "trainer_name": payment.trainer_name,
        "payment_method": payment.payment_method,
        "pay_amount": float(payment.pay_amount),
        "pending_payment": float(payment.pending_payment),
        "pay_date": payment.pay_date.strftime("%Y-%m-%d"),
        "due_date": payment.due_date.strftime("%Y-%m-%d"),
    }


# Delete a trainer payment
@app.delete("/trainerpayment/{payment_id}", response_model=dict)
def delete_trainer_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = db.query(TrainerPayment).filter(TrainerPayment.id == payment_id).first()
    if not db_payment:
        raise HTTPException(status_code=404, detail="Trainer payment not found")
    db.delete(db_payment)
    db.commit()
    return {"message": f"Trainer payment with ID {payment_id} deleted successfully"}
    
# ========== REFUND CRUD OPERATIONS ==========

# Create refund (already done)
@app.post("/refund", response_model=RefundResponse)
def create_refund(refund: RefundCreate, db: Session = Depends(get_db)):
    new_refund = Refund(**refund.dict())
    db.add(new_refund)
    db.commit()
    db.refresh(new_refund)
    return new_refund


# Get all refunds
@app.get("/refund", response_model=list[RefundResponse])
def get_all_refunds(db: Session = Depends(get_db)):
    return db.query(Refund).all()


# Get refund by ID
@app.get("/refund/{refund_id}", response_model=RefundResponse)
def get_refund(refund_id: int, db: Session = Depends(get_db)):
    refund = db.query(Refund).get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    return refund


# Update refund
@app.put("/refund/{refund_id}", response_model=RefundResponse)
def update_refund(refund_id: int, updated_data: RefundUpdate, db: Session = Depends(get_db)):
    refund = db.query(Refund).get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    for key, value in updated_data.dict().items():
        setattr(refund, key, value)
    
    db.commit()
    db.refresh(refund)
    return refund


# Delete refund
@app.delete("/refund/{refund_id}")
def delete_refund(refund_id: int, db: Session = Depends(get_db)):
    refund = db.query(Refund).get(refund_id)
    if not refund:
        raise HTTPException(status_code=404, detail="Refund not found")
    
    db.delete(refund)
    db.commit()
    return {"message": "Refund deleted successfully"}
