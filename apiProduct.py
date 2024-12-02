import uvicorn
from fastapi import FastAPI, Body, Query, HTTPException, UploadFile, File
from typing import *
from pydantic import *
# import json
from sqlalchemy import create_engine, Column, Integer, String, DATE, ForeignKey, func, desc
from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import text
from psycopg2 import *

engine = create_engine("postgresql+psycopg2://postgres:Fathima%402808@localhost/BookSales", echo=True)

Session = sessionmaker(bind=engine)
session = Session()

base = declarative_base()

class corrected(base):
    __tablename__ = "corrected"
    code_id = Column(Integer, primary_key=True)
    correct_code_block = Column(String)

class incorrected(base):
    __tablename__ = "incorrected"
    code_id = Column(Integer, primary_key=True)
    incorrect_code_block = Column(String)

def correctedSyntax(code):
    braces = list()
    for eachChar in code:
        if eachChar == "{":
            braces.append("{")
        elif eachChar == "}":
            if len(braces) == 0:
                return False
            braces.pop()
    if len(braces) == 0:
        return True
    else:
        return False

app = FastAPI()

@app.post("/tasks/add")
async def complierCpp(file: UploadFile=File(...)):
    content = await file.read()
    result = content.decode("utf-8")
    
    codeBlock = result.split("@@")
    correctedList = list()
    inCorrectedList = list()
    
    for code in codeBlock:
        errorFree = correctedSyntax(code)
        
        if(errorFree):
            correctedList.append(code)
        else:
            inCorrectedList.append(code)
    
    result = bool()
    
    try:
        for code in correctedList:
            codeSql = corrected(correct_code_block=code)
            session.add(codeSql)
            session.commit()
        for code in inCorrectedList:
            codeSql = incorrected(incorrect_code_block=code)
            session.add(codeSql)
            session.commit()
        result = True
    except Exception as e:
        result = False
    
    if(result):
        return {"Status code": 200, "Message": "Successfully Updated the data"}
    else:
        return {"Status code": 500, "Message": "Error Occurred during the Sever Interaction"}        


@app.get("/tasks")

async def getCpp(complied: bool = Query(default=None)):
    response = list()
    success = bool()
    try:
        if(complied == True):
            results = session.query(corrected).all()
            for code in results:
                response.append({code.code_id: code.correct_code_block})
            success = True
        elif(complied == False):
            results = session.query(incorrected).all()
            for code in results:
                response.append({code.code_id: code.incorrect_code_block})
            success = True
        else:
            results = session.query(corrected).all()
            for code in results:
                response.append({"correctedCode": {code.code_id: code.correct_code_block}})
            success = True
            results = session.query(incorrected).all()
            for code in results:
                response.append({"IncorrectedCode": {code.code_id: code.incorrect_code_block}})
            success = True
    except:
        success = False
    if(success):
        return {"status code": 200, "response": response}
    else:
        return {"Status code": 500, "Message": "Error Occurred during the Sever Interaction"}        


# @app.put("/tasks/update")
# async def putCpp(Index: int = Body(...), code: str = Body(...)):
#     try: 
#         total_records = session.query(func.count(incorrected.code_id)).scalar()
#         if (Index>0 and Index<= total_records):
#             record_to_update = session.query(incorrected).filter(incorrected.code_id == Index).first()
#             if record_to_update:
#                 record_to_update.incorrected.incorrect_code_block = code
#                 session.commit()
#         else:
#             raise HTTPException(status_code=400, detail="The index is either out of range or negative input")
#     except Exception as e:
#         return {"Status code": 500, "Message": "Error Occurred during the Sever Interaction"}        
    
#     error_free = correctedSyntax(code)
#     if(error_free):
#         code = corrected(correct_code_block=code)
#         session.add(code)
#         session.commit()
#         record_to_delete = session.query(incorrected).filter(incorrected.code_id == Index).first()
#         if record_to_delete:
#             session.delete(record_to_delete)
#             session.commit()       
    
#     raise HTTPException(status_code=200,detail="The code has been updated successfully")
    
@app.put("/tasks/update")
async def putCpp(Index: int = Body(...), code: str = Body(...)):
    try:
        # Fetch the record from the `incorrected` table
        record_to_update = session.query(incorrected).filter(incorrected.code_id == Index).first()

        if not record_to_update:
            raise HTTPException(status_code=404, detail="Record not found")

        # Update the record with the new code
        record_to_update.incorrect_code_block = code

        # Check if the updated code is error-free
        error_free = correctedSyntax(code)

        if error_free:
            # Move the record to the `corrected` table
            corrected_record = corrected(correct_code_block=code)
            session.add(corrected_record)

            # Remove the record from `incorrected`
            session.delete(record_to_update)

        session.commit()  # Commit all changes in a single transaction
        return {"status_code": 200, "message": "The code has been updated successfully"}

    except HTTPException as he:
        # Raise HTTP exceptions with specific details
        raise he
    except Exception as e:
        session.rollback()  # Rollback on any error
        return {"status_code": 500, "message": f"An error occurred: {str(e)}"}

if __name__ == '__main__':
    uvicorn.run(app,port=8080)

a: str = "rasheed "

a.rstrip()