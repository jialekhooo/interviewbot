from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.post import DBPost
from app.models.auth import DBUser
from app.schemas.post import Post, PostCreate, PostUpdate
from app.routers.auth import get_current_active_user
from app.schemas.auth import User

router = APIRouter()

@router.post("/posts", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new post tagged to the logged-in user"""
    # Get the full user record to get the user_id
    user_record = db.query(DBUser).filter(DBUser.username == current_user.username).first()
    if not user_record:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create the post
    db_post = DBPost(
        content=post.content,
        user_id=user_record.id,
        username=user_record.username,
        image_url=post.image_url,
        video_url=post.video_url,
        file_url=post.file_url
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts", response_model=List[Post])
async def get_posts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all posts (public feed)"""
    posts = db.query(DBPost).order_by(DBPost.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/posts/me", response_model=List[Post])
async def get_my_posts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get posts by the current logged-in user"""
    posts = db.query(DBPost).filter(DBPost.username == current_user.username).order_by(DBPost.created_at.desc()).all()
    return posts

@router.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a specific post by ID"""
    post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.put("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a post (only by the owner)"""
    db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if the current user is the owner
    if db_post.username != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")
    
    # Update fields
    if post_update.content is not None:
        db_post.content = post_update.content
    if post_update.image_url is not None:
        db_post.image_url = post_update.image_url
    if post_update.video_url is not None:
        db_post.video_url = post_update.video_url
    if post_update.file_url is not None:
        db_post.file_url = post_update.file_url
    
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a post (only by the owner)"""
    db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if the current user is the owner
    if db_post.username != current_user.username:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(db_post)
    db.commit()
    return None
