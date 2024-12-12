from typing import List, Optional
from fastapi import HTTPException, status
from app.dto.login_dto import LoginRequestDTO
from app.model.admin_model import Admin
from app.repo.admin_repo import AdminRepo
from app.utils.jwt_utils import create_access_token
from app.utils.password_utils import hash_password, verify_password


class AdminService:

    VALID_FEATURE_LIST = ["MAIN","DEVICE_STATS","CONTENT","USER_STATS"]

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
        
        if result.get("role","ADMIN") == "ADMIN" and result.get("status", "PENDING") != "ACCEPTED":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Your account has not been accepted by the superadmin. Please contact support."
            )
        
        # Verify the hashed password
        if not verify_password(loginRequestDTO.password, result["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")
        
        # Dynamically construct payload
        payload = {
            "admin_id": str(result["_id"]),
            "role": result["role"],
        }

        domain_name: Optional[str] = result.get("domain_name")
        if domain_name:
            payload["domain_name"] = domain_name

        feature_list: Optional[List[str]] = result.get("feature_list")
        if feature_list:
            payload["feature_list"] = feature_list

        access_token = create_access_token(payload)
        
        return {"access_token": access_token}
    
    @staticmethod
    async def verify_admin(admin_id: str, new_status: str):
        admin = await AdminRepo.find_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Admin with ID {admin_id} not found."
            )

        # Update the admin's status
        update_result = await AdminRepo.update_admin_status(admin_id, new_status)
        if not update_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update admin status."
            )

        return {"admin_id": admin_id, "status": new_status}
    
    @staticmethod
    async def assign_feature_access(admin_id: str, feature_list: List[str]):
        """
        Assign feature access to an admin by updating the feature list.
        """
        try:
            # Check if all features in feature_list are valid
            invalid_features = [feature for feature in feature_list if feature not in AdminService.VALID_FEATURE_LIST]
            if invalid_features:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid features: {', '.join(invalid_features)}. "
                        f"Allowed features: {', '.join(AdminService.VALID_FEATURE_LIST)}"
                )

            admin = await AdminRepo.find_admin_by_id(admin_id)
            if not admin:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Admin with ID {admin_id} not found."
                )

            # Update the admin's feature list
            update_dict = {"feature_list": feature_list}
            update_result = await AdminRepo.update_admin(admin_id, update_dict)
            if not update_result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update feature access for the admin. Please try again later."
                )

            return {"message": "Feature access assigned successfully.", "admin_id": admin_id, "features": feature_list}

        except HTTPException as e:
            # Re-raise HTTP exceptions for consistent handling
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )



