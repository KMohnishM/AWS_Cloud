# Manual Steps to Complete Reorganization

To complete the reorganization of the project, please follow these manual steps:

1. **Copy Image Files**
   - Copy all image files from `Images/` to `docs/Images/`:
     - `Images/architecture.jpg` → `docs/Images/architecture.jpg`
     - `Images/image.png` → `docs/Images/image.png`
     - `Images/Picture1.jpg` → `docs/Images/Picture1.jpg`
     - `Images/Picture2.jpg` → `docs/Images/Picture2.jpg`

2. **Clean Up Old Directories**
   After confirming that the project works with the new structure, you can remove the following directories:
   - `/main_host/`
   - `/ml_service/`
   - `/patient/`
   - `/Images/`
   - `/alertmanager/`
   - Files in the root that have been moved:
     - `/prometheus.yml`
     - `/alert.rules.yml`

3. **Test the Project**
   - Run the setup script: `chmod +x scripts/setup.sh && ./scripts/setup.sh`
   - Start the containers: `docker-compose up --build`
   - Verify that all services start correctly

4. **Update Any Remaining References**
   - Check for any remaining references to old file paths in your code
   - Update image references in markdown files if needed

Note: The binary files (images) couldn't be automatically moved by the script and need to be manually copied to maintain their integrity.