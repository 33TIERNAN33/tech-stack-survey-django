Final Project Checkpoint 2

## Task 1:

[Github Project Repo](https://github.com/33TIERNAN33/CS408ProjectRepo)  
[Github V2 Tag](https://github.com/33TIERNAN33/CS408ProjectRepo/releases/tag/v2)  
[Project Live Demo URL](http://54.245.50.134)

## Task 2:

Below is the output of my git diff between v1 and v2:  
$ git diff \--shortstat v1 v2  
 14 files changed, 1101 insertions(+), 139 deletions(-)

Summary of changes:

* Implemented the core Django models for the project, including user profiles, donors, survivors, items, and item requests.  
* Added the initial database migration so the schema can be created and updated through Django migrations.  
* Registered the new models in the Django admin panel to support easier management and testing.  
* Created a shared base template with a common header and footer to support consistent layout across the site.  
* Refactored the landing page to use the shared base template instead of duplicating layout code.  
* Added placeholder routed pages for Available Inventory, Requested Items, and Distributed Items so the application navigation now matches the planned structure.  
* Expanded test coverage to verify the home page layout, navigation structure, and model defaults.  
* Updated the deployment script so server updates more cleanly stop old processes, refresh code, rebuild the virtual environment, reinstall dependencies, run migrations, validate the project, and restart services.  
* Added gunicorn to the project requirements so deployment matches the production service configuration.

Schedule Progress:  
I am currently on track with the schedule laid out in my project specification and have completed the main goals planned for Checkpoint 2\. This checkpoint was focused on building the Django foundation of the application, including the data models, project structure, and shared template system. Those pieces are now in place, which gives me a solid base for the next stages of the project.  
In addition to meeting the checkpoint goals, I also improved the deployment workflow by making the server update script more reliable and easier to use for future code updates on AWS. This puts the project in a good position going into Checkpoint 3, where I plan to focus on authentication and role-based permissions. The project is moving from the planning and structure phase into the stage where core application features can now be built on top of the foundation completed here.  
[Project Specification](https://docs.google.com/document/d/1cKJoqwXAiZDKLOppWXlPa-SNdz0E9Nk_D0BbIeDkHX4/edit?usp=sharing)

Task 3:  
Demo:   
In the video, I demonstrate:

* The project repository on GitHub with the new Checkpoint 2 changes.  
* The Git tag for v2.  
* The Git diff summary between v1 and v2.  
* The Django project structure for the CareTrack application.  
* The new Django models and initial migration for the project database structure.  
* The shared base template with the common header and footer.  
* The landing page and the routed placeholder pages for Available Inventory, Requested Items, and Distributed Items.  
* The updated deployment script used to refresh the AWS server more cleanly.  
* The application running after the Checkpoint 2 updates.