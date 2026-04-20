Final Project Checkpoint 5

## Task 1:

Project status: completed locally in the CS408ProjectRepo working copy.

The project is currently local and has not yet been pushed to GitHub for the Checkpoint 5 tag. After this local version is pushed, the v5 release tag can be created in GitHub and the AWS EC2 server can pull the same code from the repository.

Planned repository/tag after push:

* Github Project Repo: https://github.com/33TIERNAN33/CS408ProjectRepo
* Github V5 Tag: to be created after pushing the local checkpoint work
* Project Live Demo URL: to be updated after the AWS server pulls the new code

## Task 2:

Below is the local output of my git diff for the Checkpoint 5 work before pushing it to GitHub:

$ git diff --shortstat

12 files changed, 363 insertions(+), 32 deletions(-)

Summary of changes:

* Added pagination to the inventory display so item lists are split across pages instead of loading as one long table.
* Added search across item name, description, category, and storage location.
* Added category filtering to the inventory and distributed item pages.
* Added optional JPEG and PNG image upload support for donated items and staff-created inventory items.
* Added upload validation for file type and the planned 2 MB maximum image size.
* Updated inventory display rows to show uploaded item images or a clear N/A placeholder when no image exists.
* Added local media settings so uploaded images work during development.
* Updated the AWS setup script so media uploads are preserved during pull/update deployments and served through Nginx at /media/.
* Added a Django migration converting the existing image_path field into a real file upload field.
* Added Checkpoint 5 tests covering pagination, search, category filtering, valid image upload, and invalid upload rejection.
* Ran the local Django test suite successfully with 18 passing tests.

Schedule Progress:

I am currently on track with the schedule laid out in my project specification and have completed the main goals planned for Checkpoint 5. This checkpoint focused on conditional retrieval and media handling. The Available Inventory page now supports paginated results, searching, and category filtering, which satisfies the conditional retrieval goals from the project specification. The Distributed Items page uses the same filtering and pagination structure for staff users.

Image upload is now functional for donation submissions and staff-created inventory records. Uploaded media is stored locally under the Django media directory, validated as JPEG or PNG, and limited to 2 MB. The inventory table displays uploaded images when available, while items without images show a simple placeholder.

Because the project is currently local, the Checkpoint 5 GitHub tag and AWS deployment update will happen later. The code has been written with that workflow in mind: the setup script now preserves the media directory during repository updates and adds an Nginx media route so uploaded files can still be served once the code is pulled onto the EC2 instance.

[Project Specification](https://docs.google.com/document/d/1cKJoqwXAiZDKLOppWXlPa-SNdz0E9Nk_D0BbIeDkHX4/edit?usp=sharing)

## Task 3:

Demo:

In the video, I will demonstrate:

* The local project repository with the new Checkpoint 5 changes.
* The local git diff summary for the checkpoint work.
* The Available Inventory page using pagination.
* Searching inventory by item text.
* Filtering inventory by category.
* Submitting a donation with an optional item image.
* Viewing the uploaded image in the inventory table.
* Attempting an invalid upload and showing that the form rejects unsupported file types.
* The local Django test suite running successfully with 18 passing tests.
* The deployment preparation changes that preserve media uploads and configure Nginx for the later AWS pull.
