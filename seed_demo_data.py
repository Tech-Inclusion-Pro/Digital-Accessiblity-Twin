"""
Seed script for AccessTwin demo data.

Creates realistic student and teacher accounts with extensive accessibility
profiles, support entries, tracking logs, and teacher-student linkages so
that every screen in the app is populated with example data.

Usage:
    cd /Users/roccocatrone/accesstwin
    python seed_demo_data.py

Demo credentials (all passwords: Demo1234):
  Students: maya, jordan, aisha, liam, sophie
  Teachers: rtorres, dkim
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import DatabaseManager
from models.auth import AuthManager
from models.user import User
from models.student_profile import StudentProfile
from models.support import SupportEntry
from models.tracking import TrackingLog
from models.document import Document
from models.evaluation import TwinEvaluation

DEMO_PASSWORD = "Demo1234"
SECURITY_Q1 = "What is your favorite book?"
SECURITY_A1 = "demo"
SECURITY_Q2 = "What city were you born in?"
SECURITY_A2 = "demo"


# ---------------------------------------------------------------------------
# Student Personas
# ---------------------------------------------------------------------------

STUDENTS = [
    # ---------------------------------------------------------------
    # 1. Maya Chen — Low vision / visual impairment
    # ---------------------------------------------------------------
    {
        "username": "maya",
        "display_name": "Maya Chen",
        "profile_name": "Maya Chen",
        "strengths": [
            {"text": "Exceptional auditory memory — can recall lengthy verbal instructions with high accuracy", "priority": "high"},
            {"text": "Strong creative writing skills; won the school short-story contest two years in a row", "priority": "high"},
            {"text": "Highly motivated self-advocate who confidently communicates her needs to new teachers", "priority": "non-negotiable"},
            {"text": "Excellent verbal reasoning and class discussion participation", "priority": "medium"},
            {"text": "Skilled at using assistive technology — independently learned JAWS and ZoomText", "priority": "non-negotiable"},
            {"text": "Strong organizational habits; keeps a tactile binder system color-coded with raised stickers", "priority": "medium"},
            {"text": "Empathetic peer mentor who helps other students with visual impairments during lunch club", "priority": "low"},
        ],
        "supports_summary": [
            "Enlarged print materials (18 pt minimum, sans-serif font)",
            "Screen magnification software (ZoomText) on all classroom devices",
            "Preferential seating within 5 feet of the board/display",
            "Audio-described videos and tactile diagrams for science labs",
            "Extended time (1.5x) on timed assessments",
            "Digital copies of all handouts provided 24 hours in advance",
        ],
        "history": [
            {"text": "Diagnosed with Stargardt disease (juvenile macular degeneration) at age 8", "priority": "non-negotiable"},
            {"text": "Received itinerant vision services from grades 3-6 at Lincoln Elementary", "priority": "medium"},
            {"text": "Transitioned to current high school with a full IEP in place since 9th grade", "priority": "high"},
            {"text": "Successfully completed driver's education alternative mobility program in 10th grade", "priority": "medium"},
            {"text": "Participated in state assistive technology expo in 2024 as a student presenter", "priority": "low"},
            {"text": "Had a brief period of social withdrawal in 9th grade; resolved with counseling support", "priority": "medium"},
            {"text": "Currently enrolled in AP English Literature and Honors Biology", "priority": "high"},
        ],
        "hopes": [
            {"text": "Attend a four-year university with a strong disability services office", "priority": "non-negotiable"},
            {"text": "Major in journalism or creative writing", "priority": "high"},
            {"text": "Learn to use refreshable braille display for future career flexibility", "priority": "high"},
            {"text": "Advocate for accessible digital textbooks at the school-district level", "priority": "medium"},
            {"text": "Participate in the school theater program with accessible scripts", "priority": "low"},
            {"text": "Develop skills for independent travel using public transportation", "priority": "medium"},
        ],
        "stakeholders": [
            {"text": "Dr. Linda Chen — Mother, primary advocate and IEP meeting participant", "priority": "non-negotiable"},
            {"text": "Mr. James Chen — Father, assists with home-based technology setup", "priority": "high"},
            {"text": "Ms. Rebecca Torres — 10th Grade English Teacher, accommodations coordinator", "priority": "high"},
            {"text": "Mr. David Kim — 8th Grade Science Teacher (past), provided tactile lab materials", "priority": "medium"},
            {"text": "Mrs. Patricia Nolan — Certified Vision Rehabilitation Therapist (CVRT)", "priority": "high"},
            {"text": "Dr. Sarah Washington — Low-Vision Ophthalmologist at Children's Eye Center", "priority": "medium"},
            {"text": "Jake Morales — Peer buddy and lab partner in Biology class", "priority": "low"},
        ],
        "support_entries": [
            {
                "category": "sensory",
                "subcategory": "visual",
                "description": "ZoomText screen magnification software (version 2024) installed on student's assigned Chromebook and classroom desktop. Magnification set to 3x with inverted colors (white text on black background). Teacher ensures all projected content is also available on student's device.",
                "udl_mapping": {"Representation": True, "Perception": True},
                "pour_mapping": {"Perceivable": True},
                "status": "active",
                "effectiveness_rating": 4.5,
            },
            {
                "category": "sensory",
                "subcategory": "visual",
                "description": "All printed handouts provided in 18-point Arial font with high-contrast formatting (black text on cream/yellow paper). PDF versions emailed to student's school account 24 hours before class so she can pre-read with her preferred settings.",
                "udl_mapping": {"Representation": True, "Perception": True},
                "pour_mapping": {"Perceivable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.8,
            },
            {
                "category": "sensory",
                "subcategory": "visual",
                "description": "Preferential seating in the first row, center position, within 5 feet of the interactive whiteboard. Desk is angled at 20 degrees using a slant board to reduce glare and neck strain when reading enlarged materials.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Perceivable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.2,
            },
            {
                "category": "technology",
                "subcategory": "assistive_tech",
                "description": "JAWS screen reader available as backup for extended reading sessions when eye fatigue occurs (typically after 45+ minutes). Student has headphones for independent use during class. Audio textbook access through Learning Ally membership.",
                "udl_mapping": {"Representation": True, "Action & Expression": True},
                "pour_mapping": {"Perceivable": True, "Robust": True},
                "status": "active",
                "effectiveness_rating": 4.0,
            },
            {
                "category": "academic",
                "subcategory": "assessment",
                "description": "Extended time (1.5x) on all timed assessments. Tests provided in digital format on personal device with magnification. Separate testing room available to reduce visual distractions and allow use of screen reader without disturbing peers.",
                "udl_mapping": {"Action & Expression": True, "Engagement": True},
                "pour_mapping": {"Operable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.6,
            },
            {
                "category": "environmental",
                "subcategory": "lighting",
                "description": "Adjustable desk lamp with warm LED light (2700K) to supplement classroom fluorescent lighting. Window blinds on Maya's side of the room kept partially closed to reduce glare on her screen. Anti-glare screen protector on Chromebook.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Perceivable": True},
                "status": "active",
                "effectiveness_rating": 3.8,
            },
        ],
    },

    # ---------------------------------------------------------------
    # 2. Jordan Williams — ADHD & Executive Function challenges
    # ---------------------------------------------------------------
    {
        "username": "jordan",
        "display_name": "Jordan Williams",
        "profile_name": "Jordan Williams",
        "strengths": [
            {"text": "Highly creative thinker — generates innovative project ideas that impress teachers", "priority": "high"},
            {"text": "Exceptional skills in hands-on and project-based learning environments", "priority": "non-negotiable"},
            {"text": "Natural leader in group work; peers gravitate toward Jordan's enthusiasm", "priority": "medium"},
            {"text": "Strong verbal communication skills and engaging class presenter", "priority": "medium"},
            {"text": "Passionate about robotics; leads the school's FIRST Robotics team", "priority": "non-negotiable"},
            {"text": "Able to hyper-focus on topics of high interest for extended periods", "priority": "high"},
            {"text": "Kind and empathetic; frequently checks in on classmates who seem upset", "priority": "low"},
            {"text": "Quick problem-solver under pressure — thrives during timed engineering challenges", "priority": "high"},
        ],
        "supports_summary": [
            "Visual task checklists and graphic organizers for multi-step assignments",
            "Movement breaks every 25 minutes during extended class periods",
            "Noise-canceling headphones during independent work time",
            "Chunked assignments with separate due dates instead of single large deadlines",
            "Fidget tools (stress ball, fidget cube) available at desk",
            "Digital calendar with automated reminders for assignments and transitions",
        ],
        "history": [
            {"text": "Diagnosed with ADHD (Combined Type) at age 10 by Dr. Rachel Morris, pediatric neuropsychologist", "priority": "non-negotiable"},
            {"text": "504 Plan in place since 5th grade; upgraded to a full IEP in 7th grade when executive function deficits became more impactful", "priority": "high"},
            {"text": "Tried methylphenidate (Concerta) in 6th grade; switched to lisdexamfetamine (Vyvanse) in 7th grade with better results", "priority": "high"},
            {"text": "Participated in a social skills group in middle school that significantly improved peer relationships", "priority": "medium"},
            {"text": "Had difficulty with long-form writing until introduced to speech-to-text software in 8th grade", "priority": "medium"},
            {"text": "Currently maintains a B+ average with supports in place; without supports, performance drops to C-/D+", "priority": "high"},
            {"text": "Won regional FIRST Robotics competition in 2024 — designed the autonomous navigation module", "priority": "medium"},
            {"text": "Struggles most in unstructured study halls and classes with primarily lecture-based instruction", "priority": "high"},
        ],
        "hopes": [
            {"text": "Study mechanical engineering or robotics at a university with strong STEM support", "priority": "non-negotiable"},
            {"text": "Continue developing executive function skills to manage college workload independently", "priority": "high"},
            {"text": "Learn to self-advocate in new academic environments without parental support", "priority": "high"},
            {"text": "Build a portfolio of engineering projects for college applications", "priority": "medium"},
            {"text": "Reduce reliance on external reminders by internalizing time-management strategies", "priority": "medium"},
            {"text": "Join a college robotics or engineering club team", "priority": "low"},
        ],
        "stakeholders": [
            {"text": "Mrs. Denise Williams — Mother, primary IEP advocate and homework accountability partner", "priority": "non-negotiable"},
            {"text": "Mr. Robert Williams — Father, coaches Jordan's weekend robotics practice sessions", "priority": "high"},
            {"text": "Ms. Rebecca Torres — English Teacher, uses chunked essay assignments that work well", "priority": "high"},
            {"text": "Dr. Rachel Morris — Neuropsychologist, conducts annual cognitive reassessments", "priority": "high"},
            {"text": "Mr. Carlos Vega — School Counselor, meets with Jordan biweekly for check-ins", "priority": "medium"},
            {"text": "Coach Andrea Pham — Robotics Team Advisor, provides mentorship and structure", "priority": "medium"},
            {"text": "Tyler Briggs — Best friend and robotics co-lead; accountability buddy for homework", "priority": "low"},
        ],
        "support_entries": [
            {
                "category": "executive_function",
                "subcategory": "organization",
                "description": "Visual task checklist provided at the start of each class period. Multi-step assignments broken into numbered sub-tasks with individual checkboxes. Teacher reviews checklist with Jordan at the start of class and checks progress at the midpoint.",
                "udl_mapping": {"Action & Expression": True, "Engagement": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.7,
            },
            {
                "category": "executive_function",
                "subcategory": "time_management",
                "description": "Digital timer displayed on desk (Time Timer visual countdown) during independent work. Assignments chunked into 15-minute work blocks with 2-minute micro-breaks. Google Calendar shared with parents, with automated reminders 24 hours and 1 hour before due dates.",
                "udl_mapping": {"Engagement": True, "Action & Expression": True},
                "pour_mapping": {"Operable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.3,
            },
            {
                "category": "sensory",
                "subcategory": "auditory",
                "description": "Noise-canceling headphones (Sony WH-1000XM5) available for independent work, test-taking, and study hall. Student may play low-volume instrumental music (brown noise or lo-fi) during writing tasks, which has been shown to improve sustained attention by approximately 40%.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.5,
            },
            {
                "category": "motor",
                "subcategory": "movement",
                "description": "Scheduled movement breaks every 25 minutes: may stand, stretch, walk to water fountain, or do 10 wall push-ups in the hallway. Wobble cushion on desk chair allows for subtle movement without leaving seat. Standing desk option available in back of classroom.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.1,
            },
            {
                "category": "cognitive",
                "subcategory": "assignment_modification",
                "description": "Long-form essays broken into four phases with separate due dates: (1) Brainstorm/outline, (2) First draft body paragraphs, (3) Introduction + conclusion, (4) Revision. Each phase graded independently. Speech-to-text (Google Voice Typing) available for drafting.",
                "udl_mapping": {"Action & Expression": True, "Representation": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.4,
            },
            {
                "category": "social_emotional",
                "subcategory": "self_regulation",
                "description": "Access to a calm-down pass (2 per class period) allowing Jordan to step into the hallway or visit the counselor's office for up to 5 minutes when feeling overwhelmed. Biweekly check-in meetings with school counselor Mr. Vega to discuss stress management and self-advocacy strategies.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 3.9,
            },
            {
                "category": "technology",
                "subcategory": "organizational_tools",
                "description": "Todoist app installed on school Chromebook and personal phone for cross-platform task management. Color-coded categories: Red = urgent, Yellow = this week, Green = long-term. Automated daily summary email sent to parents. Teacher posts all assignments to Google Classroom with structured templates.",
                "udl_mapping": {"Action & Expression": True, "Engagement": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.2,
            },
        ],
    },

    # ---------------------------------------------------------------
    # 3. Aisha Okafor — Deaf / Hard of Hearing
    # ---------------------------------------------------------------
    {
        "username": "aisha",
        "display_name": "Aisha Okafor",
        "profile_name": "Aisha Okafor",
        "strengths": [
            {"text": "Bilingual in American Sign Language (ASL) and written English — bridges Deaf and hearing communities", "priority": "non-negotiable"},
            {"text": "Exceptional visual-spatial reasoning; excels at geometry, data visualization, and graphic design", "priority": "high"},
            {"text": "Strong reading comprehension skills — reads at two grade levels above her peers", "priority": "medium"},
            {"text": "Confident self-advocate who educates classmates about Deaf culture during awareness week", "priority": "non-negotiable"},
            {"text": "Talented digital artist; her work has been displayed at the district art show", "priority": "high"},
            {"text": "Highly observant — notices body language and social cues that others miss", "priority": "medium"},
            {"text": "Disciplined study habits; maintains a 3.8 GPA with consistent effort", "priority": "medium"},
        ],
        "supports_summary": [
            "ASL interpreter present during all instructional periods and assemblies",
            "Real-time captioning (CART) for video content and guest speakers",
            "FM system (Roger Pen) used by teacher during lectures and discussions",
            "Visual alerts for fire alarms, class transitions, and announcements",
            "Note-taking buddy or teacher-provided guided notes for each lesson",
            "Preferential seating with clear sightline to interpreter and teacher",
        ],
        "history": [
            {"text": "Born with bilateral sensorineural hearing loss (severe-to-profound); identified through newborn hearing screening", "priority": "non-negotiable"},
            {"text": "Received bilateral cochlear implants at age 2; uses them consistently but relies primarily on ASL for complex communication", "priority": "non-negotiable"},
            {"text": "Attended a bilingual (ASL/English) preschool program at the state School for the Deaf", "priority": "high"},
            {"text": "Mainstreamed into general education in 1st grade with a full-time interpreter", "priority": "high"},
            {"text": "Speech-language therapy twice weekly from ages 3-12; now receives consultation services only", "priority": "medium"},
            {"text": "Active member of the school's Deaf and Hard of Hearing student club since 9th grade", "priority": "medium"},
            {"text": "Participated in National Association of the Deaf youth leadership camp, summer 2024", "priority": "low"},
            {"text": "Experienced interpreter staffing gaps during 9th grade that temporarily affected her performance in science class", "priority": "high"},
        ],
        "hopes": [
            {"text": "Attend Gallaudet University or RIT/NTID for a degree in graphic design or UX accessibility", "priority": "non-negotiable"},
            {"text": "Become a UX designer specializing in accessible and inclusive digital products", "priority": "high"},
            {"text": "Mentor younger Deaf students transitioning to mainstream schools", "priority": "medium"},
            {"text": "Create an ASL tutorial app for hearing students and teachers", "priority": "high"},
            {"text": "Advocate for universal captioning in all school video content", "priority": "non-negotiable"},
            {"text": "Travel internationally and connect with Deaf communities in other countries", "priority": "low"},
        ],
        "stakeholders": [
            {"text": "Mrs. Funke Okafor — Mother, fluent ASL signer, active IEP participant", "priority": "non-negotiable"},
            {"text": "Mr. Emeka Okafor — Father, learning ASL, provides technology support at home", "priority": "high"},
            {"text": "Ms. Keisha Brown — Certified ASL Interpreter, assigned full-time", "priority": "non-negotiable"},
            {"text": "Dr. Amanda Liu — Educational Audiologist, manages cochlear implant programming", "priority": "high"},
            {"text": "Ms. Rebecca Torres — English Teacher, provides visual-first lesson plans", "priority": "medium"},
            {"text": "Mr. David Kim — Science Teacher, collaborates on captioned lab demos", "priority": "medium"},
            {"text": "Priya Sharma — Best friend and co-founder of school Deaf awareness club", "priority": "low"},
        ],
        "support_entries": [
            {
                "category": "communication",
                "subcategory": "sign_language",
                "description": "Certified ASL interpreter (Ms. Keisha Brown) present during all instructional time, including labs, assemblies, field trips, and parent-teacher conferences. Interpreter positioned at a 45-degree angle from the teacher so Aisha can see both simultaneously. Backup interpreter (Mr. Tom Reyes) available for absences.",
                "udl_mapping": {"Representation": True, "Engagement": True},
                "pour_mapping": {"Perceivable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.9,
            },
            {
                "category": "sensory",
                "subcategory": "auditory",
                "description": "Roger Pen FM system used by all teachers during instruction. Teacher clips transmitter to collar; audio streams directly to Aisha's cochlear implant processors. System reduces background noise by approximately 15 dB, improving speech-to-noise ratio significantly in noisy environments like the cafeteria or gym.",
                "udl_mapping": {"Representation": True, "Perception": True},
                "pour_mapping": {"Perceivable": True},
                "status": "active",
                "effectiveness_rating": 4.3,
            },
            {
                "category": "technology",
                "subcategory": "captioning",
                "description": "Real-time captioning (CART — Communication Access Realtime Translation) provided for all video content, guest speakers, and virtual assemblies. Otter.ai used for auto-captioning during informal discussions and study groups. All teacher-created videos must include accurate captions (not auto-generated) reviewed before posting.",
                "udl_mapping": {"Representation": True, "Perception": True},
                "pour_mapping": {"Perceivable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.6,
            },
            {
                "category": "environmental",
                "subcategory": "visual_alerts",
                "description": "Visual strobe alert system installed in Aisha's primary classrooms, the gym, and the art studio for fire alarms and lockdown drills. Vibrating wristband alert (paired with school PA system) for class transition bells and urgent announcements. Teacher uses hand-raise signal to get attention before speaking.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Perceivable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.7,
            },
            {
                "category": "academic",
                "subcategory": "note_taking",
                "description": "Teacher-provided guided notes with key vocabulary and diagrams pre-filled, leaving space for Aisha to add details during class. Note-taking buddy (Priya Sharma) shares her notes via Google Docs after each class. Teacher posts all slide decks to Google Classroom before class begins so Aisha can preview content and prepare questions.",
                "udl_mapping": {"Representation": True, "Action & Expression": True},
                "pour_mapping": {"Understandable": True, "Perceivable": True},
                "status": "active",
                "effectiveness_rating": 4.5,
            },
            {
                "category": "social_emotional",
                "subcategory": "peer_connection",
                "description": "Deaf and Hard of Hearing student club meets weekly with faculty advisor. ASL signs of the week posted in Aisha's classrooms to encourage hearing peers to learn basic signs. Aisha paired with a hearing buddy during group projects who ensures she is included in side conversations and real-time decisions.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.1,
            },
        ],
    },

    # ---------------------------------------------------------------
    # 4. Liam Rodriguez — Autism Spectrum + Sensory Processing
    # ---------------------------------------------------------------
    {
        "username": "liam",
        "display_name": "Liam Rodriguez",
        "profile_name": "Liam Rodriguez",
        "strengths": [
            {"text": "Encyclopedic knowledge of marine biology — can identify over 200 species of coral reef fish", "priority": "non-negotiable"},
            {"text": "Exceptional long-term memory for factual information and sequences", "priority": "high"},
            {"text": "Highly detail-oriented; produces meticulous lab reports and data tables", "priority": "high"},
            {"text": "Honest, reliable, and deeply rule-following — peers trust him completely", "priority": "medium"},
            {"text": "Strong pattern recognition skills; excels at math, coding, and logic puzzles", "priority": "high"},
            {"text": "Passionate about environmental conservation; volunteers at the local aquarium monthly", "priority": "non-negotiable"},
            {"text": "Capable of intense, sustained focus when working on preferred topics", "priority": "medium"},
            {"text": "Gentle and caring with animals; aspires to work in marine conservation", "priority": "medium"},
        ],
        "supports_summary": [
            "Visual schedule displayed on desk showing daily routine and transitions",
            "Advance notice (5-minute warning) before activity transitions",
            "Sensory break room available with weighted blanket and dim lighting",
            "Social stories and role-playing scripts for new or unexpected situations",
            "Reduced sensory input environment (back corner seat, noise-dampening panels)",
            "Choice board for demonstrating learning (written, oral, visual, or project-based)",
        ],
        "history": [
            {"text": "Diagnosed with Autism Spectrum Disorder (Level 1 — formerly Asperger's) at age 6 by developmental pediatrician Dr. Maria Gonzales", "priority": "non-negotiable"},
            {"text": "Sensory Processing Disorder identified concurrently; occupational therapy from ages 6-11", "priority": "non-negotiable"},
            {"text": "IEP in place since kindergarten; goals shifted from behavioral to academic/social in middle school", "priority": "high"},
            {"text": "Significant difficulty with unstructured social situations; participated in a pragmatic language group from grades 4-7", "priority": "high"},
            {"text": "Had a meltdown during a surprise fire drill in 7th grade — led to implementation of advance-warning protocol", "priority": "high"},
            {"text": "Successfully completed a marine biology research project in 9th grade that was presented at the state science fair", "priority": "medium"},
            {"text": "Currently taking Honors Biology and Algebra 2; struggles most in English class with abstract literary analysis", "priority": "medium"},
            {"text": "Has a therapy dog (Bruno) at home that provides significant emotional regulation support", "priority": "high"},
        ],
        "hopes": [
            {"text": "Study marine biology or environmental science at a coastal university", "priority": "non-negotiable"},
            {"text": "Work at a marine research station or aquarium after college", "priority": "high"},
            {"text": "Learn to navigate new social environments (college, workplace) with less anxiety", "priority": "high"},
            {"text": "Develop independent living skills including cooking, laundry, and public transit use", "priority": "medium"},
            {"text": "Continue volunteering with marine conservation organizations", "priority": "medium"},
            {"text": "Create a marine biology YouTube channel or blog to share knowledge with others", "priority": "low"},
        ],
        "stakeholders": [
            {"text": "Mrs. Elena Rodriguez — Mother, primary IEP contact, drives to aquarium volunteering", "priority": "non-negotiable"},
            {"text": "Mr. Carlos Rodriguez — Father, builds sensory-friendly spaces at home", "priority": "high"},
            {"text": "Dr. Maria Gonzales — Developmental Pediatrician, annual reassessments", "priority": "high"},
            {"text": "Ms. Rebecca Torres — English Teacher, provides structured literary analysis frameworks", "priority": "medium"},
            {"text": "Mr. David Kim — Science Teacher, mentor for marine biology research project", "priority": "high"},
            {"text": "Mrs. Joanne Park — Occupational Therapist (consultation basis)", "priority": "medium"},
            {"text": "Dr. Neil Harrison — School Psychologist, social skills coaching biweekly", "priority": "high"},
            {"text": "Hannah Liu — Peer buddy in English class, helps with group discussion navigation", "priority": "low"},
        ],
        "support_entries": [
            {
                "category": "cognitive",
                "subcategory": "visual_supports",
                "description": "Laminated visual daily schedule on desk updated each morning by the classroom aide. Shows class periods, transitions, special events (assemblies, fire drills) with exact times. Changes highlighted in yellow. Five-minute verbal and visual countdown warning given before every transition between activities.",
                "udl_mapping": {"Representation": True, "Engagement": True},
                "pour_mapping": {"Understandable": True, "Perceivable": True},
                "status": "active",
                "effectiveness_rating": 4.8,
            },
            {
                "category": "sensory",
                "subcategory": "environmental",
                "description": "Assigned seat in back-left corner of classroom, away from hallway door noise and fluorescent light flicker. Noise-dampening acoustic panels installed on adjacent wall. Desk has a privacy carrel available (student's choice to use) for reducing visual overstimulation during tests or independent work.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Perceivable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.4,
            },
            {
                "category": "sensory",
                "subcategory": "regulation",
                "description": "Access to the sensory break room (Room 112) with a pass — up to 3 visits per day, 10 minutes each. Room contains weighted blanket (12 lb), noise-canceling headphones, dim adjustable lighting, bean bag chair, and fidget tools. Student may self-initiate break or be prompted by teacher when signs of dysregulation are observed (hand flapping, rocking, covering ears).",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.6,
            },
            {
                "category": "communication",
                "subcategory": "social_skills",
                "description": "Social stories provided before any new or unexpected situation (substitute teacher, schedule change, field trip). Role-playing scripts practiced with school psychologist Dr. Harrison during biweekly sessions. Conversation starter cards available in pocket for unstructured times (lunch, recess, group work). Peer buddy Hannah assigned for English class discussions.",
                "udl_mapping": {"Engagement": True, "Representation": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.0,
            },
            {
                "category": "cognitive",
                "subcategory": "academic_supports",
                "description": "Choice board for demonstrating learning: Liam may choose written essay, oral presentation with notes, visual poster/infographic, or hands-on project for any major assessment. For literary analysis in English, teacher provides a structured graphic organizer with sentence starters (e.g., 'The author uses [device] to convey [theme] because...').",
                "udl_mapping": {"Action & Expression": True, "Representation": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.3,
            },
            {
                "category": "environmental",
                "subcategory": "transitions",
                "description": "Advance notice protocol: all schedule changes communicated to Liam and his parents at least 24 hours in advance when possible. For fire drills, Liam is notified the morning of the drill (not the exact time, but that it will happen today). Transition objects (a small marine animal figurine) can be carried between classes for comfort.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Understandable": True, "Operable": True},
                "status": "active",
                "effectiveness_rating": 4.5,
            },
            {
                "category": "social_emotional",
                "subcategory": "emotional_regulation",
                "description": "Zones of Regulation framework used across all classes. Liam has a personal 'regulation toolkit' card on his desk listing strategies for each zone: Blue (tired) = stand and stretch; Green (calm) = continue working; Yellow (anxious) = use fidget or request break; Red (overwhelmed) = show red card to teacher and go to Room 112.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.2,
            },
        ],
    },

    # ---------------------------------------------------------------
    # 5. Sophie Bennett — Cerebral Palsy (Physical Disability)
    # ---------------------------------------------------------------
    {
        "username": "sophie",
        "display_name": "Sophie Bennett",
        "profile_name": "Sophie Bennett",
        "strengths": [
            {"text": "Brilliant mathematical mind — performs mental calculations faster than most of her peers", "priority": "high"},
            {"text": "Eloquent speaker and debater; captain of the school debate team for two years", "priority": "non-negotiable"},
            {"text": "Resourceful problem-solver who adapts quickly when a tool or method doesn't work", "priority": "high"},
            {"text": "Strong academic performer across all subjects; 3.9 GPA", "priority": "medium"},
            {"text": "Natural leader who organizes accessibility awareness campaigns at school", "priority": "non-negotiable"},
            {"text": "Excellent writing skills using voice-to-text — writes detailed, persuasive essays", "priority": "high"},
            {"text": "Tech-savvy; independently learned to customize assistive technology settings", "priority": "medium"},
            {"text": "Resilient and positive attitude; inspires peers with her determination", "priority": "medium"},
        ],
        "supports_summary": [
            "Voice-to-text software (Dragon NaturallySpeaking) for all written work",
            "Adaptive keyboard (large keys, keyguard) and trackball mouse",
            "Physical accessibility: ramp access, elevator key, accessible desk and lab station",
            "Extended time (2x) on handwritten or keyboard-intensive assessments",
            "Classroom aide assistance for lab setup and material manipulation",
            "Wheelchair-accessible seating and workspace in all classrooms",
        ],
        "history": [
            {"text": "Diagnosed with spastic diplegic cerebral palsy at 18 months; primarily affects lower limbs and fine motor control in hands", "priority": "non-negotiable"},
            {"text": "Uses a power wheelchair for mobility since age 5; manual wheelchair as backup", "priority": "non-negotiable"},
            {"text": "Occupational therapy ongoing since age 2; currently receives OT twice monthly for fine motor maintenance", "priority": "high"},
            {"text": "Physical therapy twice weekly focused on muscle tone management and positioning", "priority": "high"},
            {"text": "Had orthopedic surgery (selective dorsal rhizotomy) at age 9, which significantly improved leg spasticity", "priority": "high"},
            {"text": "Transitioned from a self-contained classroom to full inclusion in 3rd grade with aide support", "priority": "medium"},
            {"text": "Participated in adaptive sports (wheelchair basketball and swimming) since 6th grade", "priority": "medium"},
            {"text": "Won the district debate championship in 10th grade — judges noted her exceptional argumentation skills", "priority": "low"},
            {"text": "Currently enrolled in AP Calculus, AP Government, and Honors English", "priority": "medium"},
        ],
        "hopes": [
            {"text": "Attend a university with excellent disability services and an accessible campus", "priority": "non-negotiable"},
            {"text": "Study pre-law or political science — aspires to become a disability rights attorney", "priority": "non-negotiable"},
            {"text": "Compete in collegiate adaptive sports (wheelchair basketball or swimming)", "priority": "medium"},
            {"text": "Advocate for improved physical accessibility in public buildings and transportation", "priority": "high"},
            {"text": "Live independently in college with appropriate support services", "priority": "high"},
            {"text": "Intern at a disability rights organization during college", "priority": "medium"},
        ],
        "stakeholders": [
            {"text": "Mrs. Jennifer Bennett — Mother, full-time advocate and medical coordinator", "priority": "non-negotiable"},
            {"text": "Mr. Mark Bennett — Father, built custom adaptive workspace at home", "priority": "high"},
            {"text": "Ms. Rebecca Torres — English Teacher, provides voice-to-text accommodations", "priority": "medium"},
            {"text": "Mr. David Kim — Science Teacher, redesigned lab stations for wheelchair access", "priority": "high"},
            {"text": "Dr. Katherine Wu — Pediatric Physiatrist at Children's Rehabilitation Center", "priority": "high"},
            {"text": "Mrs. Lisa Chang — Occupational Therapist, fine motor and adaptive tech specialist", "priority": "high"},
            {"text": "Mr. Derek Thompson — Physical Therapist, mobility and positioning", "priority": "medium"},
            {"text": "Ms. Angela Martinez — Classroom Aide, assists with lab setup and material handling", "priority": "non-negotiable"},
            {"text": "Ryan Cooper — Debate team co-captain and study partner", "priority": "low"},
        ],
        "support_entries": [
            {
                "category": "technology",
                "subcategory": "voice_input",
                "description": "Dragon NaturallySpeaking Professional (v16) installed on student's dedicated laptop. Custom vocabulary profile trained for academic terminology (calculus, government, literary terms). Used for all essay writing, test responses, and note-taking. Backup: Google Voice Typing on Chromebook. Teacher accepts voice-recorded responses for short-answer questions when typing fatigue occurs.",
                "udl_mapping": {"Action & Expression": True},
                "pour_mapping": {"Operable": True, "Robust": True},
                "status": "active",
                "effectiveness_rating": 4.7,
            },
            {
                "category": "motor",
                "subcategory": "adaptive_equipment",
                "description": "Large-key adaptive keyboard (BigKeys LX) with keyguard overlay to prevent accidental key strikes. Kensington Expert trackball mouse replaces standard mouse. All devices mounted on adjustable arm attached to wheelchair tray for optimal positioning. Stylus holder for touchscreen interaction when needed.",
                "udl_mapping": {"Action & Expression": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.4,
            },
            {
                "category": "environmental",
                "subcategory": "physical_access",
                "description": "Height-adjustable accessible desk in every classroom (adjusts 24-36 inches) to accommodate power wheelchair. Elevator key for all multi-story buildings. Ramp access verified and maintained for all routes between classes. Priority dismissal (2 minutes early) to navigate hallways before crowd. Lab station adapted with lowered countertops and accessible sink.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True, "Perceivable": True},
                "status": "active",
                "effectiveness_rating": 4.6,
            },
            {
                "category": "academic",
                "subcategory": "assessment",
                "description": "Extended time (2x) on all timed assessments involving writing or keyboard input. For math assessments, teacher provides enlarged graph paper and Sophie may dictate solutions to the aide or use an on-screen graphing tool. All test materials provided in digital format for screen interaction.",
                "udl_mapping": {"Action & Expression": True, "Engagement": True},
                "pour_mapping": {"Operable": True, "Understandable": True},
                "status": "active",
                "effectiveness_rating": 4.5,
            },
            {
                "category": "motor",
                "subcategory": "aide_support",
                "description": "Classroom aide (Ms. Angela Martinez) provides physical assistance for science lab setup (handling chemicals, adjusting microscope, cutting materials), carrying books/materials between classes, and setting up/packing away adaptive equipment. Aide does NOT provide academic support — Sophie completes all intellectual work independently.",
                "udl_mapping": {"Engagement": True, "Action & Expression": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.3,
            },
            {
                "category": "physical",
                "subcategory": "positioning",
                "description": "Custom seating system in power wheelchair evaluated quarterly by PT. Includes lateral trunk supports, abductor wedge, and tilt-in-space function for pressure relief. Student performs weight shifts every 30 minutes (timer on wheelchair). Standing frame available in the PT room for 20-minute sessions during study hall to maintain bone density and hip alignment.",
                "udl_mapping": {"Engagement": True},
                "pour_mapping": {"Operable": True},
                "status": "active",
                "effectiveness_rating": 4.1,
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Teacher Personas
# ---------------------------------------------------------------------------

TEACHERS = [
    {
        "username": "rtorres",
        "display_name": "Ms. Rebecca Torres",
    },
    {
        "username": "dkim",
        "display_name": "Mr. David Kim",
    },
]


# ---------------------------------------------------------------------------
# Tracking Logs — rich narratives from student and teacher perspectives
# ---------------------------------------------------------------------------

def build_student_tracking_logs():
    """Return a list of (student_username, support_index, role, impl_notes, outcome_notes, days_ago)."""
    return [
        # Maya — student self-logs
        ("maya", 0, "student", "Used ZoomText today during the poetry analysis in English class. The 3x magnification worked perfectly for the projected poem, and I could read along on my own screen. When we switched to small-group discussion, I minimized the magnification to 2x so I could see my group members' faces more easily.", "Effectiveness rated: 5/5", 1),
        ("maya", 1, "student", "Ms. Torres emailed me the handout for tomorrow's vocabulary lesson. The PDF was already in 18-point Arial — no reformatting needed. I pre-read it in about 15 minutes and highlighted words I want to discuss. This advance access makes such a huge difference.", "Effectiveness rated: 5/5", 3),
        ("maya", 4, "student", "Had the unit test today in the separate testing room. The extended time helped, but I only needed about 1.3x instead of the full 1.5x. I'm getting faster with the digital format. The room was quiet and my screen settings were perfect. Felt confident about my answers.", "Effectiveness rated: 4/5", 5),
        ("maya", 5, "student", "The desk lamp ran out of battery halfway through Biology. The fluorescent lights caused some glare on my screen and I got a headache. Need to remember to charge the lamp every weekend. Asked Mr. Kim if we could get a backup plug-in lamp.", "Effectiveness rated: 3/5", 7),

        # Jordan — student self-logs
        ("jordan", 0, "student", "The checklist today had 6 items for the essay workshop. I got through 4 of them before I lost focus. Ms. Torres checked in at the midpoint and helped me re-prioritize — I skipped item 3 (peer review) temporarily and went straight to drafting, which was the right call. Finished items 1, 2, 4, and 5.", "Effectiveness rated: 4/5", 1),
        ("jordan", 3, "student", "Movement break after 25 minutes worked great today. I did wall push-ups in the hallway and came back feeling re-energized. The wobble cushion is okay but I think I prefer standing at the back desk for the second half of long periods.", "Effectiveness rated: 4/5", 2),
        ("jordan", 2, "student", "Forgot my headphones today and independent work time was rough. The classroom was noisy because of the group project happening on the other side. I tried to focus without them but only got through half the reading. Need a backup pair in my locker.", "Effectiveness rated: 2/5", 4),
        ("jordan", 6, "student", "Todoist sent me a reminder about the history project due Friday and I actually started working on it three days early! That never would have happened before. Mom said she got the daily summary email too and didn't need to remind me. This system is really working.", "Effectiveness rated: 5/5", 6),

        # Aisha — student self-logs
        ("aisha", 0, "student", "Ms. Brown interpreted the entire guest speaker assembly today. The speaker talked fast and used a lot of idioms which were tricky to interpret in real-time, but Ms. Brown is experienced and handled it well. She fingerspelled the unfamiliar technical terms and I could figure them out from context.", "Effectiveness rated: 5/5", 1),
        ("aisha", 2, "student", "The auto-captioning on the science video was terrible — about 60% accurate. Lots of scientific terms were completely wrong. Mr. Kim paused the video and Ms. Brown interpreted the key parts instead. We need to push for pre-captioned science videos from the publisher.", "Effectiveness rated: 3/5", 3),
        ("aisha", 4, "student", "Got the guided notes for tomorrow's English lesson from Ms. Torres' Google Classroom post. The vocabulary section was really helpful because I could look up the signs for the new words before class. Priya shared her notes too, and between the two I felt fully prepared.", "Effectiveness rated: 5/5", 5),
        ("aisha", 5, "student", "ASL club meeting went great! We taught 15 hearing students the signs for common classroom phrases. Two teachers also dropped by to learn. I feel like the school is becoming more Deaf-friendly. Next week we're doing a Deaf culture trivia game.", "Effectiveness rated: 4/5", 8),

        # Liam — student self-logs
        ("liam", 0, "student", "The visual schedule was really important today because there was a schedule change — we had an assembly during 3rd period instead of 4th. The aide updated my schedule first thing in the morning and highlighted the change in yellow. I felt prepared and the transition went smoothly.", "Effectiveness rated: 5/5", 1),
        ("liam", 2, "student", "Used the sensory break room during English class today. We were doing a group discussion about symbolism in the novel and the noise level was getting too high for me. I showed my yellow card and went to Room 112 for 8 minutes. The weighted blanket helped me calm down and I came back ready to participate in the written reflection.", "Effectiveness rated: 5/5", 2),
        ("liam", 4, "student", "For the English essay on 'The Great Gatsby,' I chose the infographic option from the choice board. I created a detailed visual showing the symbolism of the green light with illustrations and short explanations. Ms. Torres said it demonstrated excellent understanding of the text. This was so much better than writing a traditional essay.", "Effectiveness rated: 5/5", 4),
        ("liam", 6, "student", "Had a tough day today. A substitute teacher didn't know about my regulation toolkit and asked me to stop using my fidget tool during class. I got anxious and went to Red zone. Showed my red card and went to Room 112. Dr. Harrison came to check on me. The substitute apologized later — they hadn't been briefed.", "Effectiveness rated: 3/5", 9),

        # Sophie — student self-logs
        ("sophie", 0, "student", "Used Dragon for the entire AP Government essay today — 1,200 words in 45 minutes. The custom vocabulary for political science terms ('judicial review,' 'gerrymandering,' 'filibuster') worked perfectly with no corrections needed. Voice-to-text is now faster for me than typing ever was.", "Effectiveness rated: 5/5", 1),
        ("sophie", 2, "student", "The elevator was out of service for maintenance today and I had to use the ramp on the other side of the building. It added 7 minutes to my transition time between 2nd and 3rd period. The priority dismissal helped but I was still 3 minutes late. The school needs to notify me about elevator maintenance in advance.", "Effectiveness rated: 3/5", 3),
        ("sophie", 4, "student", "Ms. Martinez helped set up the chemistry lab today — measured out chemicals and adjusted the microscope height for my wheelchair tray. I did all the observations, data recording, and analysis myself. The adapted lab station worked well but the sink faucet was hard to reach even at the lowered counter.", "Effectiveness rated: 4/5", 5),
        ("sophie", 5, "student", "Did my standing frame session during study hall today — 20 minutes. PT said my hip alignment looks good and we can continue the current schedule. Standing frame time is actually when I do my best thinking for debate prep. I've started using it as brainstorming time.", "Effectiveness rated: 4/5", 7),
    ]


def build_teacher_tracking_logs():
    """Return a list of (student_username, support_index, impl_notes, outcome_notes, days_ago)."""
    return [
        # Ms. Torres (rtorres) logs about her students
        ("maya", 1, "Prepared enlarged handout for Monday's lesson on rhetorical analysis. Used 18pt Arial on cream cardstock as specified. Also created a fully tagged PDF version and emailed it to Maya at 3pm on Sunday — well within the 24-hour advance window. Included image descriptions for all example advertisements used in the lesson.", "Maya came to class prepared and participated actively in the analysis discussion. She had already annotated the PDF on her tablet and raised two thoughtful questions about ethos in advertising. The advance access is clearly making a significant difference in her engagement.", 2),
        ("jordan", 0, "Created a 5-step checklist for the persuasive essay assignment: (1) Choose topic and write thesis statement, (2) Outline 3 body paragraph arguments with evidence, (3) Draft body paragraphs using speech-to-text, (4) Write introduction and conclusion, (5) Peer review and revision. Each step has its own due date this week. Reviewed the checklist with Jordan at 8:05am.", "Jordan completed steps 1 and 2 on day one, which is excellent — usually he struggles to start. The speech-to-text option for step 3 seemed to reduce his resistance to drafting. He told me the separate due dates make it 'feel like five small assignments instead of one scary one.' Will continue this approach for all major essays.", 3),
        ("aisha", 4, "Posted guided notes for the Shakespeare unit to Google Classroom 48 hours before the lesson. Included a glossary of archaic terms with modern English equivalents and corresponding ASL video links. Ms. Brown and I pre-met for 15 minutes to review the Shakespearean vocabulary so she could prepare her interpretation.", "Aisha's comprehension of the Shakespeare excerpt was on par with the strongest readers in class. The pre-meeting with Ms. Brown was invaluable — her interpretation of iambic pentameter was much smoother than previous attempts without preparation. The ASL glossary links were also used by three other students who found them helpful.", 4),
        ("liam", 4, "Offered Liam the choice board for the 'Great Gatsby' symbolism essay. Options: (A) Traditional 5-paragraph essay, (B) Oral presentation with visual aids, (C) Infographic with written explanations, (D) Recorded video analysis. Liam chose option C (infographic) immediately and seemed visibly relieved. Provided the graphic organizer with sentence starters as an additional scaffold.", "Liam's infographic was one of the strongest submissions in the class. His visual representation of the green light symbolism included four detailed illustrations with 50-100 word explanations each. The graphic organizer sentence starters helped him structure his writing concisely. He was engaged for the full 45-minute work period — no sensory breaks needed.", 5),
        ("sophie", 0, "Set up Dragon NaturallySpeaking on the classroom laptop for today's in-class essay. Ran the voice calibration with Sophie before class started (takes 3 minutes). Provided noise-canceling headset with microphone to reduce ambient classroom noise during dictation. Reminded class to keep volume moderate during Sophie's dictation periods.", "Sophie completed the essay prompt in 40 minutes — faster than 80% of the class. Her dictated essay was well-organized, with clear topic sentences and strong evidence. The custom vocabulary profile meant zero correction time for government terms. She mentioned that the headset microphone picks up her voice much better than the laptop's built-in mic.", 2),

        # Mr. Kim (dkim) logs
        ("maya", 3, "Provided audio descriptions for today's Biology lab video on cell division. Created a supplementary tactile diagram using raised-line drawing paper and puffy paint for the mitosis stages. Tested the JAWS compatibility with the digital lab worksheet before class. Set up Maya's desk lamp and verified anti-glare settings.", "Maya followed the cell division process accurately using the tactile diagram and identified all phases correctly on the lab quiz. She mentioned that the audio descriptions were most helpful during the time-lapse microscopy footage, which is inherently visual. The tactile diagram is now a permanent resource she can review for the unit test.", 6),
        ("aisha", 1, "Tested Roger Pen FM system before the chemistry lecture. Noticed the battery was at 15% — swapped with backup unit. Wore the transmitter clipped to my collar throughout the lesson. Made sure to face Aisha's direction when speaking and pause before transitioning to a new topic so Ms. Brown could signal the topic change.", "Aisha reported that the FM audio was clear throughout the 50-minute lecture. She was able to follow the chemistry equations on the board while receiving audio narration directly. Pausing at topic transitions made a noticeable difference — Ms. Brown confirmed it gave her time to set up the conceptual frame in ASL before I continued.", 4),
        ("liam", 5, "Notified Liam's parents last night about today's fire drill (scheduled for 10:15am). Updated his visual schedule first thing in the morning to show 'Fire Drill' in the 3rd period slot with a yellow highlight. Briefed the substitute para about the regulation toolkit and red-card protocol. Placed noise-canceling headphones on his desk before the drill.", "The fire drill went smoothly — a major improvement from last year's incident. Liam put on the headphones before the alarm sounded and walked calmly to the assembly point with his class. He did not show signs of distress. His mother emailed to say the advance notice made all the difference; Liam talked about the drill matter-of-factly at dinner.", 8),
        ("sophie", 2, "Redesigned Lab Station 4 for today's chemistry experiment: lowered the counter to 28 inches, moved the hot plate to the front edge within arm's reach, and set up a mirror above the beaker so Sophie could observe reactions from wheelchair height. Ms. Martinez pre-measured hazardous chemicals as a safety precaution.", "Sophie completed the entire lab procedure independently (with Ms. Martinez handling chemical measurement for safety). She recorded all observations using Dragon on her laptop, which was mounted on the wheelchair tray next to the lab station. The mirror setup worked perfectly — she could see the color changes in the solution without needing to stand. This configuration should be documented as our standard for wheelchair-accessible labs.", 5),
    ]


# ---------------------------------------------------------------------------
# AI Evaluation mock data for teacher-evaluated documents
# ---------------------------------------------------------------------------

MOCK_EVALUATIONS = [
    {
        "student": "maya",
        "filename": "English_10_Poetry_Unit_Lesson_Plan.pdf",
        "purpose": "Evaluate poetry unit lesson plan for visual accessibility. Lesson includes projected poems, printed handouts, and video analysis of spoken word performances.",
        "ai_analysis": {
            "overall_accessibility_score": 7.2,
            "summary": "This lesson plan has good foundational accessibility but needs improvements in three areas: (1) projected poems need higher contrast and larger font, (2) video content lacks audio descriptions for visual elements in spoken word performances, (3) printed handouts should use cream/yellow paper to reduce glare for the student's low vision condition.",
            "strengths_identified": [
                "Digital copies of poems are provided in advance",
                "Multiple response modes are offered (written, oral, visual)",
                "Teacher reads poems aloud in addition to displaying text",
            ],
            "barriers_identified": [
                "Projected text uses 14pt serif font on white background — below student's 18pt sans-serif requirement",
                "Spoken word videos lack audio description tracks",
                "Small-group discussion relies on reading shared handout that is only available in standard print",
                "Interactive whiteboard annotations are in light colors that may not be visible to the student",
            ],
        },
        "suggestions": [
            {"suggestion": "Increase projected text to 24pt Arial on dark background (white text on navy)", "confidence": 0.95, "priority": "high"},
            {"suggestion": "Provide audio-described versions of spoken word videos or create teacher narration", "confidence": 0.88, "priority": "high"},
            {"suggestion": "Print small-group handouts on cream paper in 18pt Arial for the student", "confidence": 0.92, "priority": "medium"},
            {"suggestion": "Use high-contrast annotation colors (yellow, white) on the interactive whiteboard", "confidence": 0.85, "priority": "medium"},
            {"suggestion": "Email digital copies of ALL materials (not just poems) 24 hours before class", "confidence": 0.90, "priority": "medium"},
        ],
    },
    {
        "student": "jordan",
        "filename": "History_Research_Project_Guidelines.docx",
        "purpose": "Evaluate research project guidelines for executive function accessibility. Project requires independent topic selection, source gathering, outline, draft, and final paper over 3 weeks.",
        "ai_analysis": {
            "overall_accessibility_score": 5.8,
            "summary": "This project guideline presents significant executive function barriers due to its single-deadline structure, lack of visual task breakdown, and minimal scaffolding for the planning phase. The 3-week timeline without intermediate checkpoints is likely to cause procrastination and last-minute stress for this student.",
            "strengths_identified": [
                "Topic selection includes a choice board with pre-approved options",
                "Research resources are curated and linked in the assignment document",
            ],
            "barriers_identified": [
                "Single due date for the entire project — no intermediate checkpoints",
                "Instructions presented as continuous text paragraphs without visual breaks",
                "No graphic organizer or outline template provided",
                "Time estimation not included — student cannot plan work sessions",
                "Rubric is at the end of the document and may be overlooked",
            ],
        },
        "suggestions": [
            {"suggestion": "Break the project into 5 phases with individual due dates and grades", "confidence": 0.96, "priority": "high"},
            {"suggestion": "Convert paragraph instructions into a numbered visual checklist with checkboxes", "confidence": 0.94, "priority": "high"},
            {"suggestion": "Provide a graphic organizer template for the outline phase", "confidence": 0.91, "priority": "high"},
            {"suggestion": "Include estimated time-per-phase (e.g., 'Topic selection: ~30 minutes')", "confidence": 0.87, "priority": "medium"},
            {"suggestion": "Move the rubric to page 1 or provide it as a separate highlighted document", "confidence": 0.83, "priority": "medium"},
            {"suggestion": "Offer speech-to-text option for the drafting phase", "confidence": 0.89, "priority": "medium"},
        ],
    },
    {
        "student": "liam",
        "filename": "Biology_Field_Trip_Permission_and_Plan.pdf",
        "purpose": "Evaluate field trip plan for sensory and communication accessibility. Trip to the natural history museum includes bus ride, guided tour, cafeteria lunch, and gift shop visit.",
        "ai_analysis": {
            "overall_accessibility_score": 4.5,
            "summary": "This field trip plan has critical accessibility gaps for a student with autism and sensory processing needs. The itinerary lacks visual schedule format, includes multiple unstructured transitions, has no sensory break plan, and does not address the noise levels in museum exhibits. The cafeteria lunch and gift shop visit are unstructured social situations that will require significant advance preparation.",
            "strengths_identified": [
                "The museum has been contacted in advance about the visit",
                "Parent chaperones are included in the plan",
            ],
            "barriers_identified": [
                "Itinerary is in paragraph form — not a visual schedule",
                "No advance social stories or visual preparation materials",
                "Bus ride has no assigned seating or sensory toolkit plan",
                "Museum exhibits with loud interactive displays are on the route",
                "Cafeteria lunch is unstructured free-choice seating",
                "Gift shop visit is crowded and overstimulating",
                "No quiet space or sensory break location identified at the museum",
                "Substitute chaperone may not know the student's regulation protocols",
            ],
        },
        "suggestions": [
            {"suggestion": "Create a visual schedule with photos of each museum location and exact times", "confidence": 0.97, "priority": "critical"},
            {"suggestion": "Write a social story about the field trip with photos of the bus, museum entrance, and exhibits", "confidence": 0.95, "priority": "critical"},
            {"suggestion": "Assign the student a window seat near the front of the bus with noise-canceling headphones", "confidence": 0.92, "priority": "high"},
            {"suggestion": "Identify a quiet room at the museum in advance as a sensory break space", "confidence": 0.94, "priority": "high"},
            {"suggestion": "Route the guided tour to avoid the loudest interactive exhibits or visit them last", "confidence": 0.88, "priority": "high"},
            {"suggestion": "Pre-assign cafeteria seating with the peer buddy in a quieter corner", "confidence": 0.86, "priority": "medium"},
            {"suggestion": "Make the gift shop visit optional and offer an alternative quiet activity", "confidence": 0.84, "priority": "medium"},
            {"suggestion": "Brief ALL chaperones on the student's regulation toolkit and red-card protocol", "confidence": 0.93, "priority": "high"},
        ],
    },
]


# ---------------------------------------------------------------------------
# Main seed function
# ---------------------------------------------------------------------------

def seed():
    db = DatabaseManager()
    auth = AuthManager(db)

    # Check if demo data already exists
    check_session = db.get_session()
    existing = check_session.query(User).filter(User.username == "maya").first()
    check_session.close()
    if existing:
        print("Demo data already exists. To re-seed, delete the database first:")
        print("  rm ~/Library/Application\\ Support/AccessTwin/accesstwin.db")
        print("  python seed_demo_data.py")
        return

    now = datetime.now(timezone.utc)
    student_profiles = {}  # username -> (user_id, profile_id, [(entry_id, ...)])

    # ------------------------------------------------------------------
    # Create student accounts and profiles
    # ------------------------------------------------------------------
    for s in STUDENTS:
        print(f"  Creating student: {s['username']} ({s['display_name']})...")

        ok, msg = auth.register(
            username=s["username"],
            password=DEMO_PASSWORD,
            role="student",
            display_name=s["display_name"],
            security_question_1=SECURITY_Q1,
            security_answer_1=SECURITY_A1,
            security_question_2=SECURITY_Q2,
            security_answer_2=SECURITY_A2,
        )
        if not ok:
            print(f"    ERROR registering {s['username']}: {msg}")
            continue

        user_id = auth.current_user.id
        auth.current_user = None  # clear without audit log to avoid session conflicts

        # Create profile and supports in a single session
        session = db.get_session()
        profile = StudentProfile(
            user_id=user_id,
            name=s["profile_name"],
            strengths_json=json.dumps(s["strengths"]),
            supports_json=json.dumps(s["supports_summary"]),
            history_json=json.dumps(s["history"]),
            hopes_json=json.dumps(s["hopes"]),
            stakeholders_json=json.dumps(s["stakeholders"]),
        )
        session.add(profile)
        session.flush()

        # Create support entries
        entries = []
        for se in s["support_entries"]:
            entry = SupportEntry(
                profile_id=profile.id,
                category=se["category"],
                subcategory=se.get("subcategory"),
                description=se["description"],
                udl_mapping=json.dumps(se.get("udl_mapping", {})),
                pour_mapping=json.dumps(se.get("pour_mapping", {})),
                status=se.get("status", "active"),
                effectiveness_rating=se.get("effectiveness_rating"),
            )
            session.add(entry)
            session.flush()
            entries.append(entry)

        session.commit()
        # Store IDs (not ORM objects) to avoid cross-session issues
        student_profiles[s["username"]] = {
            "user_id": user_id,
            "profile_id": profile.id,
            "profile_name": profile.name,
            "profile": s,  # raw dict for twin export
            "entry_ids": [e.id for e in entries],
            "entries_raw": s["support_entries"],
        }
        session.close()

    print(f"  Created {len(student_profiles)} student accounts with profiles.\n")

    # ------------------------------------------------------------------
    # Create student tracking logs
    # ------------------------------------------------------------------
    print("  Creating student experience logs...")
    session = db.get_session()
    student_log_count = 0
    for username, sup_idx, role, impl, outcome, days_ago in build_student_tracking_logs():
        if username not in student_profiles:
            continue
        sp = student_profiles[username]
        if sup_idx >= len(sp["entry_ids"]):
            continue
        log = TrackingLog(
            profile_id=sp["profile_id"],
            logged_by_role=role,
            support_id=sp["entry_ids"][sup_idx],
            implementation_notes=impl,
            outcome_notes=outcome,
            created_at=now - timedelta(days=days_ago, hours=10, minutes=30),
        )
        session.add(log)
        student_log_count += 1

    session.commit()
    session.close()
    print(f"  Created {student_log_count} student experience logs.\n")

    # ------------------------------------------------------------------
    # Create teacher accounts
    # ------------------------------------------------------------------
    teacher_users = {}  # username -> user_id
    for t in TEACHERS:
        print(f"  Creating teacher: {t['username']} ({t['display_name']})...")
        ok, msg = auth.register(
            username=t["username"],
            password=DEMO_PASSWORD,
            role="teacher",
            display_name=t["display_name"],
            security_question_1=SECURITY_Q1,
            security_answer_1=SECURITY_A1,
            security_question_2=SECURITY_Q2,
            security_answer_2=SECURITY_A2,
        )
        if not ok:
            print(f"    ERROR registering {t['username']}: {msg}")
            continue
        teacher_users[t["username"]] = auth.current_user.id
        auth.current_user = None  # clear without audit log

    print(f"  Created {len(teacher_users)} teacher accounts.\n")

    # ------------------------------------------------------------------
    # Import student twins into teacher accounts (create Document + TwinEvaluation)
    # ------------------------------------------------------------------
    print("  Linking students to teachers via twin imports...")

    # Ms. Torres teaches Maya, Jordan, Aisha, Liam, Sophie
    # Mr. Kim teaches Maya, Aisha, Liam, Sophie
    teacher_student_map = {
        "rtorres": ["maya", "jordan", "aisha", "liam", "sophie"],
        "dkim": ["maya", "aisha", "liam", "sophie"],
    }

    session = db.get_session()
    for teacher_username, student_usernames in teacher_student_map.items():
        if teacher_username not in teacher_users:
            continue
        teacher_user_id = teacher_users[teacher_username]

        for student_username in student_usernames:
            if student_username not in student_profiles:
                continue
            sp = student_profiles[student_username]
            raw = sp["profile"]

            # Build a twin JSON blob (mimicking what export produces)
            twin_data = {
                "version": "1.0",
                "profile": {
                    "name": sp["profile_name"],
                    "strengths": raw["strengths"],
                    "supports_summary": raw["supports_summary"],
                    "history": raw["history"],
                    "hopes": raw["hopes"],
                    "stakeholders": raw["stakeholders"],
                },
                "support_entries": [
                    {
                        "category": se["category"],
                        "subcategory": se.get("subcategory"),
                        "description": se["description"],
                        "udl_mapping": se.get("udl_mapping", {}),
                        "pour_mapping": se.get("pour_mapping", {}),
                        "status": se.get("status", "active"),
                        "effectiveness_rating": se.get("effectiveness_rating"),
                    }
                    for se in raw["support_entries"]
                ],
            }

            file_blob = json.dumps(twin_data).encode("utf-8")
            doc = Document(
                teacher_user_id=teacher_user_id,
                filename=f"{sp['profile_name'].replace(' ', '_')}_twin.json",
                file_type="json",
                file_blob=file_blob,
                purpose_description="twin_import",
            )
            session.add(doc)
            session.flush()

            twin_eval = TwinEvaluation(
                document_id=doc.id,
                student_profile_id=sp["profile_id"],
            )
            session.add(twin_eval)

    session.commit()
    session.close()
    print("  Twin imports linked.\n")

    # ------------------------------------------------------------------
    # Create teacher tracking logs
    # ------------------------------------------------------------------
    print("  Creating teacher implementation logs...")
    session = db.get_session()
    teacher_log_count = 0

    teacher_log_data = build_teacher_tracking_logs()

    for idx, (username, sup_idx, impl, outcome, days_ago) in enumerate(teacher_log_data):
        if username not in student_profiles:
            continue
        sp = student_profiles[username]
        if sup_idx >= len(sp["entry_ids"]):
            continue

        # First 5 logs are Torres, last 4 are Kim
        if idx < 5:
            teacher_username = "rtorres"
        else:
            teacher_username = "dkim"

        log = TrackingLog(
            profile_id=sp["profile_id"],
            logged_by_role="teacher",
            support_id=sp["entry_ids"][sup_idx],
            implementation_notes=impl,
            outcome_notes=outcome,
            created_at=now - timedelta(days=days_ago, hours=14, minutes=15),
        )
        session.add(log)
        teacher_log_count += 1

    session.commit()
    session.close()
    print(f"  Created {teacher_log_count} teacher implementation logs.\n")

    # ------------------------------------------------------------------
    # Create mock AI evaluations for documents
    # ------------------------------------------------------------------
    print("  Creating AI evaluation records for documents...")
    session = db.get_session()
    eval_count = 0

    for ev_data in MOCK_EVALUATIONS:
        student_username = ev_data["student"]
        if student_username not in student_profiles:
            continue
        sp = student_profiles[student_username]

        # Figure out which teacher to assign this to
        if student_username == "jordan":
            teacher_username = "rtorres"
        elif student_username in ("maya", "liam"):
            # Maya poetry = Torres, Liam field trip = Kim
            teacher_username = "rtorres" if "Poetry" in ev_data["filename"] else "dkim"
        else:
            teacher_username = "rtorres"

        if teacher_username not in teacher_users:
            continue
        teacher_user_id = teacher_users[teacher_username]

        # Create document
        doc = Document(
            teacher_user_id=teacher_user_id,
            filename=ev_data["filename"],
            file_type=ev_data["filename"].rsplit(".", 1)[-1],
            file_blob=f"[Placeholder content for {ev_data['filename']}]".encode("utf-8"),
            purpose_description=ev_data["purpose"],
        )
        session.add(doc)
        session.flush()

        # Create evaluation
        twin_eval = TwinEvaluation(
            document_id=doc.id,
            student_profile_id=sp["profile_id"],
            ai_analysis_json=json.dumps(ev_data["ai_analysis"]),
            suggestions_json=json.dumps(ev_data["suggestions"]),
            confidence_scores=json.dumps({
                "overall": ev_data["ai_analysis"]["overall_accessibility_score"] / 10,
            }),
            reasoning_json=json.dumps({
                "method": "UDL + POUR framework cross-reference",
                "model": "Demo analysis (seed data)",
            }),
        )
        session.add(twin_eval)
        eval_count += 1

    session.commit()
    session.close()
    print(f"  Created {eval_count} AI evaluation records.\n")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("=" * 60)
    print("  ACCESSTWIN DEMO DATA SEEDED SUCCESSFULLY")
    print("=" * 60)
    print()
    print("  All demo accounts use password: Demo1234")
    print()
    print("  STUDENT ACCOUNTS:")
    print("  -------------------------------------------------")
    for s in STUDENTS:
        print(f"    Username: {s['username']:10s}  Name: {s['display_name']}")
    print()
    print("  TEACHER ACCOUNTS:")
    print("  -------------------------------------------------")
    for t in TEACHERS:
        print(f"    Username: {t['username']:10s}  Name: {t['display_name']}")
    print()
    print("  Each student has:")
    print("    - A fully populated accessibility profile")
    print("    - 6-7 detailed support entries with UDL/POUR mappings")
    print("    - 4 experience tracking logs with detailed notes")
    print()
    print("  Each teacher has:")
    print("    - Imported student twins visible on their dashboard")
    print("    - Implementation tracking logs with detailed notes")
    print("    - AI evaluation records for uploaded documents")
    print()
    print("  PRIVACY-PRESERVING AI COACH:")
    print("  -------------------------------------------------")
    print("    - Teachers see only broad themes and categories (no specifics)")
    print("    - 'Consult Coach' opens the AI Digital Accessibility Coach")
    print("    - Coach reads full data privately, responds with safe guidance")
    print("    - Configure AI via Home > Configure AI or the coach dialog")
    print("    - Supports: Ollama, LM Studio, GPT4All, OpenAI, Anthropic")
    print()
    print("  Run the app:  python main.py")
    print("=" * 60)


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  AccessTwin Demo Data Seeder")
    print("=" * 60)
    print()
    seed()
