Final Project Checkpoint 3

## Task 1:

[Github Project Repo](https://github.com/33TIERNAN33/CS408ProjectRepo)  
[Github V3 Tag](https://github.com/33TIERNAN33/CS408ProjectRepo/releases/tag/v3)  
[Project Live Demo URL](http://54.245.50.134)

## Task 2:

Below is the output of my git diff between v2 and v3:  
$ git diff \--shortstat v2 v3  
 12 files changed, 441 insertions(+), 6 deletions(-)

Summary of changes:

* Implemented user authentication for the CareTrack application, including login, logout, and account registration functionality.    
* Added a registration form that creates new users and stores role information through the UserProfile model.    
* Added a user dashboard page so authenticated users can view their account role and approval status.    
* Implemented role-based access control for protected pages using the existing UserProfile role structure.    
* Restricted staff-only pages so they now require an approved staff account instead of being publicly accessible.    
* Updated the shared site navigation and landing page to support the new authentication flow.    
* Added templates for login, registration, dashboard, and access-restricted handling.    
* Expanded automated tests to verify registration, login, redirects for anonymous users, permission enforcement, and approved staff access.

Schedule Progress:  
I am currently on track with the schedule laid out in my project specification and have completed the main goals I had planned for Checkpoint 3\. This checkpoint was focused on implementing authentication and role-based permissions, and those core features are now working in the project. Users can now create accounts, log in, log out, and access a personal dashboard, while protected pages can now be limited based on account role and approval status.    
This checkpoint moves the project beyond basic structure and into actual application security and access control, which is an important step before building the main CRUD workflows. With authentication and permissions now in place, the project is in a good position for Checkpoint 4, where I plan to focus on making the donation form functional and continuing the core database-backed application behavior.  
[Project Specification](https://docs.google.com/document/d/1cKJoqwXAiZDKLOppWXlPa-SNdz0E9Nk_D0BbIeDkHX4/edit?usp=sharing)

Task 3:  
Demo:   
In the video, I demonstrate:

* The project repository on GitHub with the new Checkpoint 3 changes.    
* The Git tag for v3.    
* The Git diff summary between v2 and v3.    
* The new login, logout, and registration functionality in the CareTrack application.    
* The user dashboard showing role and approval status.    
* The updated navigation and landing page reflecting the new authentication flow.    
* A protected staff-only page showing role-based access control in action.    
* The application running after the Checkpoint 3 updates.