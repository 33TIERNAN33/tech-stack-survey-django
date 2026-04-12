Final Project Checkpoint 4

## Task 1:

[Github Project Repo](https://github.com/33TIERNAN33/CS408ProjectRepo)  
[Github V4 Tag](https://github.com/33TIERNAN33/CS408ProjectRepo/releases/tag/v4)  
[Project Live Demo URL](http://54.245.50.134)

## Task 2:

Below is the combined diff summary between v3 and the Checkpoint 4 working update before tagging, including newly added template and documentation files:  
$ git diff --shortstat v3  
 11 files changed, 459 insertions(+), 18 deletions(-)

Summary of changes:

* Added a functional database-backed donation form that creates donor and inventory item records.
* Replaced the Available Inventory placeholder page with a database-backed inventory list.
* Added approved-staff CRUD routes for creating, editing, and deleting inventory items.
* Added distributed-item retrieval for approved staff accounts using the same inventory display template.
* Updated the shared navigation and dashboard links so users can submit donations and staff can manage inventory.
* Added Checkpoint 4 tests covering donation submission, inventory retrieval, staff create/update/delete behavior, and access control.
* Ran the local Django test suite successfully with 14 passing tests.

Schedule Progress:  
I am currently on track with the schedule laid out in my project specification and have completed the main goals planned for Checkpoint 4. This checkpoint was focused on moving beyond authentication into database-backed application behavior. The donation form now writes donor and item information into the SQLite database, and the inventory page now retrieves and displays actual records instead of placeholder text.

CRUD functionality is now operational for staff users. Approved staff accounts can create inventory records, update item details and distribution status, and delete inventory entries. Non-staff users are blocked from staff-only CRUD pages through the same role-based access control system completed in Checkpoint 3. Local testing was also expanded and verified, with the Django test suite passing after the Checkpoint 4 changes.

[Project Specification](https://docs.google.com/document/d/1cKJoqwXAiZDKLOppWXlPa-SNdz0E9Nk_D0BbIeDkHX4/edit?usp=sharing)

Task 3:  
Demo:  
In the video, I demonstrate:

* The project repository on GitHub with the new Checkpoint 4 changes.
* The Git tag for v4.
* The Git diff summary between v3 and v4.
* The donation form creating donor and inventory item records in the database.
* The Available Inventory page retrieving and displaying database records.
* Approved staff access to create, edit, and delete inventory items.
* A non-staff account being blocked from staff-only CRUD pages.
* The local Django test suite running successfully with 14 passing tests.
