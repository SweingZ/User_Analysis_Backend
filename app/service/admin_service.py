from fastapi import HTTPException, status
from app.dto.login_dto import LoginRequestDTO
from app.model.admin_model import Admin
from app.repo.admin_repo import AdminRepo
from app.utils.password_utils import hash_password, verify_password

class AdminService:

    @staticmethod
    async def register_admin(admin: Admin):
        if not admin.username:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username cannot be empty.")
        if not admin.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty.")
        
        existing_admin = await AdminRepo.find_admin(admin.username)
        if existing_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists.")
        
        try:
            # Hash the password before saving it
            admin.password = hash_password(admin.password)
            result = await AdminRepo.insert_user(admin)
            if result:
                return {"message": "Admin Registered Successfully"}
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register admin.")
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error Occurred: {str(e)}")
    
    @staticmethod
    async def login_admin(loginRequestDTO: LoginRequestDTO):
        if not loginRequestDTO.username or not loginRequestDTO.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both username and password are required.")
        
        result = await AdminRepo.find_admin(loginRequestDTO.username)
        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Admin Found with that username.")
        
        # Verify the hashed password
        if not verify_password(loginRequestDTO.password, result["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")
        
        return {"admin_id": str(result["_id"])}
