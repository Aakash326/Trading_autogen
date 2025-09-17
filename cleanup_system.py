#!/usr/bin/env python3
"""
System Cleanup Script
Moves unnecessary files to archive folder, keeping only essential workflows
"""

import os
import shutil
from datetime import datetime

def create_archive_folder():
    """Create archive folder if it doesn't exist"""
    archive_path = "archive"
    if not os.path.exists(archive_path):
        os.makedirs(archive_path)
        print(f"✅ Created archive folder: {archive_path}")
    return archive_path

def move_file_to_archive(file_path, archive_path):
    """Move a file to archive folder"""
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        archive_file_path = os.path.join(archive_path, filename)
        
        # Add timestamp if file already exists in archive
        if os.path.exists(archive_file_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file_path = os.path.join(archive_path, f"{name}_{timestamp}{ext}")
        
        shutil.move(file_path, archive_file_path)
        print(f"📦 Moved: {file_path} → {archive_file_path}")
        return True
    else:
        print(f"⚠️ File not found: {file_path}")
        return False

def main():
    """Main cleanup function"""
    print("🧹 Starting System Cleanup")
    print("=" * 50)
    print("Moving unnecessary files to archive folder...")
    
    # Create archive folder
    archive_path = create_archive_folder()
    
    # Files to archive (unnecessary for core functionality)
    files_to_archive = [
        # Extra workflow files
        "src/workflows/integrated_analysis.py",
        "src/workflows/interactive_workflow.py",
        
        # Extra application files  
        "application.py",
        "application_standalone.py",
        "start_app.py",
        
        # Test and demo files
        "test_hybrid_system.py",
        "test_workflow_simplified.py", 
        "demo_interactive.py",
        
        # Documentation files (can be archived)
        "WORKFLOW_ARCHITECTURE.md",
        "SYSTEM_FILES_EXPLAINED.md",
        "CLEAN_SYSTEM_STRUCTURE.md"
    ]
    
    print(f"\n📋 Files to archive ({len(files_to_archive)} total):")
    for file_path in files_to_archive:
        print(f"  - {file_path}")
    
    # Ask for confirmation
    response = input(f"\n❓ Move these {len(files_to_archive)} files to archive? (y/n): ").strip().lower()
    
    if response in ['y', 'yes']:
        print(f"\n🔄 Moving files...")
        moved_count = 0
        
        for file_path in files_to_archive:
            if move_file_to_archive(file_path, archive_path):
                moved_count += 1
        
        print(f"\n✅ Cleanup Complete!")
        print(f"📦 Moved {moved_count} files to archive")
        print(f"📁 Archive location: {archive_path}/")
        
        # Show what remains
        print(f"\n🎯 REMAINING CORE FILES:")
        core_files = [
            "start_interactive.py (Main console app)",
            "application_hybrid.py (Web API)",
            "src/workflows/hybrid_team.py (13-agent system)",
            "src/teams/teams.py (7-agent system)",
            "src/agents/* (All agent files)",
            "src/model/model.py (AI configuration)",
            "requirements.txt (Dependencies)",
            ".env (API keys)"
        ]
        
        for file_desc in core_files:
            print(f"  ✅ {file_desc}")
        
        print(f"\n🚀 Your system is now clean with only essential files!")
        print(f"\n📖 Usage:")
        print(f"  • New system: python3 start_interactive.py")
        print(f"  • Old system: python3 src/teams/teams.py")
        print(f"  • Web API: python3 application_hybrid.py")
        
    else:
        print(f"❌ Cleanup cancelled. No files were moved.")
    
    print(f"\n👋 Cleanup script finished.")

if __name__ == "__main__":
    main()