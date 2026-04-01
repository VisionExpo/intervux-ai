import re
import os

filepath = "backend/api/routes/candidate_routes.py"
with open(filepath, "r", encoding="utf-8") as f:
    text = f.read()

# Add sqlalchemy select
text = text.replace("from backend.db.database import SessionLocal", "from backend.db.database import AsyncSessionLocal\nfrom sqlalchemy import select")

# candidate_signup
old_signup = """    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == candidate_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        try:
            db_user = User(
                email=candidate_data.email,
                password_hash=hash_password(candidate_data.password),
                name=candidate_data.name,
                role=Role.CANDIDATE,
            )
            db.add(db_user)
            db.flush()

            user_id = f"candidate-{db_user.id}"

            profile = CandidateProfile(
                user_id=user_id,
                name=candidate_data.name,
                skills="[]",
                mock_interviews_remaining=3,
            )
            db.add(profile)
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=500, detail="Signup failed, please try again")

        user_data = {
            "user_id": user_id,
            "email": candidate_data.email,
            "name": candidate_data.name,
            "role": Role.CANDIDATE,
        }
        return create_token_pair(user_data)

    finally:
        db.close()"""
        
new_signup = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).filter(User.email == candidate_data.email))
        existing_user = res.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        try:
            db_user = User(
                email=candidate_data.email,
                password_hash=hash_password(candidate_data.password),
                name=candidate_data.name,
                role=Role.CANDIDATE,
            )
            db.add(db_user)
            await db.flush()

            user_id = f"candidate-{db_user.id}"

            profile = CandidateProfile(
                user_id=user_id,
                name=candidate_data.name,
                skills="[]",
                mock_interviews_remaining=3,
            )
            db.add(profile)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Signup failed, please try again")

        user_data = {
            "user_id": user_id,
            "email": candidate_data.email,
            "name": candidate_data.name,
            "role": Role.CANDIDATE,
        }
        return create_token_pair(user_data)"""
text = text.replace(old_signup, new_signup)

# get_candidate_profile
old_gcp = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score or _calculate_profile_score(profile),
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )
    finally:
        db.close()"""
new_gcp = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score or _calculate_profile_score(profile),
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )"""
text = text.replace(old_gcp, new_gcp)

# update_candidate_profile
old_ucp = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile_update.name is not None:
            profile.name = profile_update.name
        if profile_update.skills is not None:
            profile.skills = json.dumps(profile_update.skills)
        if profile_update.experience_years is not None:
            profile.experience_years = profile_update.experience_years
        if profile_update.education is not None:
            profile.education = profile_update.education
        if profile_update.github_url is not None:
            profile.github_url = profile_update.github_url
        if profile_update.linkedin_url is not None:
            profile.linkedin_url = profile_update.linkedin_url

        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(profile)

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score,
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )
    finally:
        db.close()"""
new_ucp = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(CandidateProfile.user_id == current_user.user_id))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile_update.name is not None:
            profile.name = profile_update.name
        if profile_update.skills is not None:
            profile.skills = json.dumps(profile_update.skills)
        if profile_update.experience_years is not None:
            profile.experience_years = profile_update.experience_years
        if profile_update.education is not None:
            profile.education = profile_update.education
        if profile_update.github_url is not None:
            profile.github_url = profile_update.github_url
        if profile_update.linkedin_url is not None:
            profile.linkedin_url = profile_update.linkedin_url

        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(profile)

        skills = json.loads(profile.skills) if profile.skills else []

        return CandidateProfileResponse(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            skills=skills,
            experience_years=profile.experience_years,
            education=profile.education,
            resume_url=profile.resume_url,
            resume_score=profile.resume_score,
            interview_score=profile.interview_score,
            profile_score=profile.profile_score,
            github_url=profile.github_url,
            linkedin_url=profile.linkedin_url,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            created_at=profile.created_at,
        )"""
text = text.replace(old_ucp, new_ucp)

# upload_resume
old_ur = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        # Save file to disk
        upload_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "uploads", "resumes", current_user.user_id
        )
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Parse via unified service in threadpool to avoid blocking event loop.
        file.file.seek(0)
        try:
            parsed: ParsedResume = await asyncio.to_thread(parse_resume_from_upload, file)
        except Exception:
            logger.exception("Resume parsing failed in candidate upload")
            parsed = ParsedResume()

        resume_score, strengths, weaknesses = _calculate_resume_score(parsed)

        resume_url = f"/uploads/resumes/{current_user.user_id}/{unique_filename}"

        profile.resume_url = resume_url
        profile.resume_score = resume_score
        profile.skills = json.dumps(parsed.skills)
        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        db.commit()

        notification = Notification(
            user_id=current_user.user_id,
            type="resume_analyzed",
            message=f"Your resume has been analyzed. Score: {resume_score:.0f}%",
        )
        db.add(notification)
        db.commit()

        return ResumeUploadResponse(
            resume_url=resume_url,
            resume_score=resume_score,
            skills=parsed.skills,
            strengths=strengths,
            weaknesses=weaknesses,
        )
    finally:
        db.close()"""
new_ur = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        # Save file to disk
        upload_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "uploads", "resumes", current_user.user_id
        )
        os.makedirs(upload_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4().hex}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Parse via unified service in threadpool to avoid blocking event loop.
        file.file.seek(0)
        try:
            parsed: ParsedResume = await asyncio.to_thread(parse_resume_from_upload, file)
        except Exception:
            logger.exception("Resume parsing failed in candidate upload")
            parsed = ParsedResume()

        resume_score, strengths, weaknesses = _calculate_resume_score(parsed)

        resume_url = f"/uploads/resumes/{current_user.user_id}/{unique_filename}"

        profile.resume_url = resume_url
        profile.resume_score = resume_score
        profile.skills = json.dumps(parsed.skills)
        profile.profile_score = _calculate_profile_score(profile)
        profile.updated_at = datetime.utcnow()

        await db.commit()

        notification = Notification(
            user_id=current_user.user_id,
            type="resume_analyzed",
            message=f"Your resume has been analyzed. Score: {resume_score:.0f}%",
        )
        db.add(notification)
        await db.commit()

        return ResumeUploadResponse(
            resume_url=resume_url,
            resume_score=resume_score,
            skills=parsed.skills,
            strengths=strengths,
            weaknesses=weaknesses,
        )"""
text = text.replace(old_ur, new_ur)

# start_mock_interview
old_smi = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile.mock_interviews_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No mock interviews remaining. Upgrade to get more.",
            )

        existing_count = db.query(MockInterview).filter(
            MockInterview.candidate_id == profile.id
        ).count()

        session_id = f"mock-{uuid.uuid4().hex}"
        mock_interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=existing_count + 1,
        )
        db.add(mock_interview)

        profile.mock_interviews_remaining -= 1

        db.commit()
        db.refresh(mock_interview)

        return MockInterviewStartResponse(
            session_id=session_id,
            message="Mock interview started. Connect to WebSocket for the interview.",
            mock_interview_id=mock_interview.id,
        )
    finally:
        db.close()"""
new_smi = """    from sqlalchemy import func
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        if profile.mock_interviews_remaining <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No mock interviews remaining. Upgrade to get more.",
            )

        count_res = await db.execute(select(func.count(MockInterview.id)).filter(
            MockInterview.candidate_id == profile.id
        ))
        existing_count = count_res.scalar()

        session_id = f"mock-{uuid.uuid4().hex}"
        mock_interview = MockInterview(
            candidate_id=profile.id,
            session_id=session_id,
            status="in_progress",
            interview_number=existing_count + 1,
        )
        db.add(mock_interview)

        profile.mock_interviews_remaining -= 1

        await db.commit()
        await db.refresh(mock_interview)

        return MockInterviewStartResponse(
            session_id=session_id,
            message="Mock interview started. Connect to WebSocket for the interview.",
            mock_interview_id=mock_interview.id,
        )"""
text = text.replace(old_smi, new_smi)

# get_mock_interview_history
old_gmih = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            return []

        interviews = (
            db.query(MockInterview)
            .filter(MockInterview.candidate_id == profile.id)
            .order_by(MockInterview.created_at.desc())
            .all()
        )

        return [
            MockInterviewResponse(
                id=i.id,
                session_id=i.session_id,
                score=i.score,
                technical_score=i.technical_score,
                communication_score=i.communication_score,
                reasoning_score=i.reasoning_score,
                status=i.status,
                interview_number=i.interview_number,
                created_at=i.created_at,
                completed_at=i.completed_at,
            )
            for i in interviews
        ]
    finally:
        db.close()"""
new_gmih = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            return []

        i_res = await db.execute(select(MockInterview)
            .filter(MockInterview.candidate_id == profile.id)
            .order_by(MockInterview.created_at.desc()))
        interviews = i_res.scalars().all()

        return [
            MockInterviewResponse(
                id=i.id,
                session_id=i.session_id,
                score=i.score,
                technical_score=i.technical_score,
                communication_score=i.communication_score,
                reasoning_score=i.reasoning_score,
                status=i.status,
                interview_number=i.interview_number,
                created_at=i.created_at,
                completed_at=i.completed_at,
            )
            for i in interviews
        ]"""
text = text.replace(old_gmih, new_gmih)

# get_mock_interview
old_gmi = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        interview = db.query(MockInterview).filter(
            MockInterview.id == interview_id,
            MockInterview.candidate_id == profile.id,
        ).first()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        return MockInterviewResponse(
            id=interview.id,
            session_id=interview.session_id,
            score=interview.score,
            technical_score=interview.technical_score,
            communication_score=interview.communication_score,
            reasoning_score=interview.reasoning_score,
            status=interview.status,
            interview_number=interview.interview_number,
            created_at=interview.created_at,
            completed_at=interview.completed_at,
        )
    finally:
        db.close()"""
new_gmi = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        i_res = await db.execute(select(MockInterview).filter(
            MockInterview.id == interview_id,
            MockInterview.candidate_id == profile.id,
        ))
        interview = i_res.scalar_one_or_none()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        return MockInterviewResponse(
            id=interview.id,
            session_id=interview.session_id,
            score=interview.score,
            technical_score=interview.technical_score,
            communication_score=interview.communication_score,
            reasoning_score=interview.reasoning_score,
            status=interview.status,
            interview_number=interview.interview_number,
            created_at=interview.created_at,
            completed_at=interview.completed_at,
        )"""
text = text.replace(old_gmi, new_gmi)

# get_notifications
old_gn = """    db = SessionLocal()
    try:
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == current_user.user_id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )

        return [
            NotificationResponse(
                id=n.id,
                type=n.type,
                message=n.message,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]
    finally:
        db.close()"""
new_gn = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Notification)
            .filter(Notification.user_id == current_user.user_id)
            .order_by(Notification.created_at.desc())
            .limit(50))
        notifications = res.scalars().all()

        return [
            NotificationResponse(
                id=n.id,
                type=n.type,
                message=n.message,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ]"""
text = text.replace(old_gn, new_gn)

# mark_notification_read
old_mnr = """    db = SessionLocal()
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.user_id,
        ).first()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.is_read = True
        db.commit()

        return {"message": "Notification marked as read"}
    finally:
        db.close()"""
new_mnr = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.user_id,
        ))
        notification = res.scalar_one_or_none()
        if not notification:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

        notification.is_read = True
        await db.commit()

        return {"message": "Notification marked as read"}"""
text = text.replace(old_mnr, new_mnr)

# get_candidate_dashboard
old_gcd = """    db = SessionLocal()
    try:
        profile = db.query(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ).first()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        recent_activity = []

        recent_interview = (
            db.query(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
            )
            .order_by(MockInterview.completed_at.desc())
            .first()
        )

        if recent_interview:
            recent_activity.append(
                f"Mock Interview #{recent_interview.interview_number} completed - Score: {recent_interview.score:.0f}"
            )

        if profile.resume_url:
            recent_activity.append("Resume analyzed")

        if profile.profile_score and profile.profile_score >= 50:
            recent_activity.append("Profile updated")

        completed_interviews = (
            db.query(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
                MockInterview.score.isnot(None),
            )
            .all()
        )

        mock_interview_score = (
            sum(i.score for i in completed_interviews) / len(completed_interviews)
            if completed_interviews
            else 0.0
        )

        return DashboardResponse(
            profile_score=profile.profile_score or 0.0,
            resume_score=profile.resume_score or 0.0,
            mock_interview_score=mock_interview_score,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            recent_activity=recent_activity,
        )
    finally:
        db.close()"""
new_gcd = """    async with AsyncSessionLocal() as db:
        res = await db.execute(select(CandidateProfile).filter(
            CandidateProfile.user_id == current_user.user_id
        ))
        profile = res.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        recent_activity = []

        i_res = await db.execute(select(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
            )
            .order_by(MockInterview.completed_at.desc()))
        recent_interview = i_res.scalars().first()

        if recent_interview:
            if recent_interview.score is not None:
                recent_activity.append(f"Mock Interview #{recent_interview.interview_number} completed - Score: {recent_interview.score:.0f}")
            else:
                recent_activity.append(f"Mock Interview #{recent_interview.interview_number} completed")


        if profile.resume_url:
            recent_activity.append("Resume analyzed")

        if profile.profile_score and profile.profile_score >= 50:
            recent_activity.append("Profile updated")

        ci_res = await db.execute(select(MockInterview)
            .filter(
                MockInterview.candidate_id == profile.id,
                MockInterview.status == "completed",
                MockInterview.score.isnot(None),
            ))
        completed_interviews = ci_res.scalars().all()

        mock_interview_score = (
            sum(i.score for i in completed_interviews) / len(completed_interviews)
            if completed_interviews
            else 0.0
        )

        return DashboardResponse(
            profile_score=profile.profile_score or 0.0,
            resume_score=profile.resume_score or 0.0,
            mock_interview_score=mock_interview_score,
            mock_interviews_remaining=profile.mock_interviews_remaining,
            recent_activity=recent_activity,
        )"""
text = text.replace(old_gcd, new_gcd)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(text)

print("SUCCESS: candidate_routes.py replaced")
