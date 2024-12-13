# Changelog
## [Version: 2.7.3] - 2024-11-25
【Feature】Add meta context management, applied to fast approval, MOA, and notification receivers filter.  
【Fix】API request node POST parameter editing rendering issue.  
【Fix】"Submit" button was not internationalized, "Return to Ticket List" button text overflow.  


## [Version: 2.7.2] - 2024-11-18
【Feature】Add a popup confirmation when deleting lines on the canvas.  
【Improved】When selecting ‘All Systems’ in the API list, remove the options for creating new and importing APIs.  
【Fix】Correct the spelling error in the OpenAPI workflow interface.  


## [Version: 2.7.1] - 2024-11-06
【Feature】Integrated pipeline management tool.  
【Improved】Ensure TEXT compatibility with JSON and Markdown formats.  
【Fix】Resolve the issue where the inputselect component cannot select conditions in the trigger.  
【Fix】Fix the issue where newly added fields in a node cannot detect from the previous node.  
【Fix】Fix the issue with the JSON component anomaly in the submission node.  


## [Version: 2.7.0] - 2024-10-10
【Feature】Notification recipient blacklist filtering.  
【Improved】Migrated the authentication information to header when calling esb, support open-paas/esb >= 2.12.20  
【Improved】Changed “My Tasks” to “My Completed” in the navigation bar.  
【Improved】Adjust default items when adding an Approval Node in the process.  
【Improved】Adjusted platform management permissions to be instance-free authentication.  
【Fixed】The navigation bar style has been standardized according to the design specifications.  
【Fixed】Modified the implementation method for exporting common API files.  
【Fixed】Fixed the issue where searching on the document list in non-home pages resulted in an error.  
【Fixed】Optimized the return path when clicking ‘Previous’ during task template editing.  
【Fixed】Fixed XSS vulnerability in tooltips component.  
【Fixed】Resolved authentication exceptions in some modules.  
【Fixed】Resolved the issue of APM deployment without data.  
【Fixed】Resolved the issue where the service visibility range was not effective.  
【Fixed】Resolved the issue of abnormal display of parent comments in the work order comments.  
【Fixed】Resolved the issue of inaccurate end time in operation analysis.  
【Fixed】Resolved the deadlock issue in the parallel gateway.  


## [Version: 2.6.30] - 2024-08-15
【Fixed】Fixed the URL Redirection Issue after Login during Project Initialization

## [Version: 2.6.29] - 2024-08-14
【Fixed】Fix the internationalization issue in permission application content.  

## [Version: 2.6.28] - 2024-08-08
【Fixed】Fix the XSS vulnerability in form submission.

## [Version: 2.6.27] - 2024-08-07
【Improved】Login in Full-Screen Mode during Project Initialization  
【Improved】Project Title Specification Adjustment  


## [Version: 2.6.26] - 2024-07-22
【Fixed】Fix the issue where an interface value of 0 causes process abnormalities.  
【Fixed】Fix the initialization exception of apigw.  

## [Version: 2.6.25] - 2024-07-19
【Fixed】Fixed the issue where the API request URL for message notifications was incorrect in certain environments.

## [Version: 2.6.24] - 2024-07-18
【Improved】Optimized the search functionality for the notification template list.  
【Fixed】Consolidated validation failure messages when creating a new service.  
【Fixed】Added non-empty validation to the pop-up for referencing common triggers.  
【Fixed】Removed the SLA filter option from the service list search.  
【Fixed】Mounted the data dictionary edit side panel to the body.  
【Fixed】Fixed the issue where the global configuration favicon was not being applied.  
【Fixed】Resolved the issue causing an exception when desc is empty while fetching role information.  
【Fixed】Fix the issue with the abnormal value retrieval during manual retry of the API node.  


## [Version: 2.6.23] - 2024-07-03
【Improved】Enabled support for clearing the search operation on the left-side field controls of the service form.  
【Improved】Removed the method of referencing common triggers from the task template triggers.  
【Improved】Remove the permissions of the submitter and node handler in the close order operation.  
【Fixed】Fixed the issue where the Message Notification Center was not displayed on the frontend.  
【Fixed】Fixed the issue where the expand/collapse icon on the left-side menu of the service list was displayed incorrectly.  
【Fixed】Added a secondary confirmation pop-up when clicking on the shadow area after editing the data dictionary without saving.  
【Fixed】Fixed the issue where the row height in the service table was not being applied.  
【Fixed】Fixed the issue where the favorite status of the frequently used services and all services cards on the homepage did not synchronize after toggling.  
【Fixed】Fixed the issue where data in the list page was not updated after editing the API.  
【Fixed】Fixed the issue where the left-side directory tree was not updated after service import.  

## [Version: 2.6.22] - 2024-06-24
【Improved】Global project settings are editable.

## [Version: 2.6.21] - 2024-06-12
【Fixed】Fixed the issue where the default project could not be edited.  
【Fixed】Fixed the issue where multiple identical services could be created by repeatedly clicking the Create Service button.  
【Fixed】Fixed the issue where the search parameter key was incorrect when filtering the service list by type.  
【Fixed】Added a maximum character limit of 1000 to the reason form in the close and suspend document operation pop-ups.  

## [Version: 2.6.20] - 2024-06-06
【Fixed】Fixed the issue where the time control position on the Operations Analysis page was calculated inaccurately.  
【Fixed】Removed the comment type switch icon from the document comment edit popup.  
【Fix】Remove personnel information from the work order interface.  
【Improved】Optimized the style for long characters in the transaction log.  
【Improved】Optimized the placeholder text for the personnel selector.  
【Improved】Added maximum height to the ticket detail table fields.  

## [Version: 2.6.19] - 2024-05-29
【Fixed】Fixed the issue where logout was not effective  
【Improved】Support for iframe loading mode implemented

## [Version: 2.6.18] - 2024-05-15
[Fixed] Resolved the issue with unprocessed node fields during joint validation  
[Fixed] Fixed the issue where there was no redirection after login  
[Fixed] Fixed the interface anomaly caused by non-existent variables on the print page  
[Improved] Added length restriction for work order closure reasons  
[Improved] Optimized indexes in the ticket table  

## [Version: 2.6.17] - 2024-05-11
[Fixed] Resolved XSS vulnerability in work order rich text  
[Improved] Unified login window interactions

## [Version: 2.6.16] - 2024-05-08
[Fixed] Fix the issue with the initialization exception in the version log.

## [Version: 2.6.15] - 2024-04-22
[Fixed] Fixed the issue where the field linkage condition judgment was incorrect.

## [Version: 2.6.14] - 2024-04-21
[Improved] Upgraded select pip dependencies for improved security

## [Version: 2.6.13] - 2024-04-17
[Fixed] Fixed the issue where the document information fields on the detail page of the repair order were not fully displayed.  
[Fixed] Fixed the issue where the directory field was not validated when creating a service.

## [Version: 2.6.12] - 2024-04-08
【Fixed】Fixed the issue of insufficient permissions for the assignee when SOPS tasks fail in parallel gateways.

## [Version: 2.6.11] - 2024-02-29
 [Improved] Fix the problem of uploading abnormality when the attachment is stored as a product library    
 [Fixed] Repair the problem of unregistered the notification center of the containerization environment  
 [Fixed] Repair the role of the initialization of the introduction authority center is an issue of abnormal emptiness  

## [Version: 2.6.10] - 2024-02-04
 [Improved] Allow to configure the timeout of permission center sdk & skip auto-authorization for resources created by admin.   
 [Fixed] Fix the problem that the import process is abnormal when it is a user group.  
 [Improved] Front-end access to message notification center

## [Version: 2.6.9] - 2024-01-07
 [Improved] Support url parameter default value on bill of lading page.    
 [Fixed] Fix the problem that the order of fields in quick approval document is not consistent with the actual one.

## [Version: 2.6.8] - 2023-11-09
 [Improved] Gateway added description  
 [Improved] Handle the problem of internationalization error when switching the list of documents quickly  
 [Improved] Gateway adds a method to get the approval result of a node  
 [Improved] The Community Edition supports the capabilities of the Approval Assistant  
 [Improved] Custom form support url new page or iframe open link  
 [Improved] Fix the problem of mobile login jumping  
 [Improved] Optimize states node rendering performance to improve interface access speeds  
 [Improved] Repair the problem that the automatic order over does not take effect when importing updates   
 [Improved] Expand the number of gthreads to optimize interface performance concurrency performance  
 [Improved] The process supports the selection of a specified variable superior  
 [Improved] Add My Managers to Work Order Management  
 [Fixed] Tips related to adding documents without permissions on the mobile side  
 [Fixed] Fix TicketLog delete logic  
 [Fixed] Fix get_service_roles ordering issue  
 [Fixed] Repair the problem of mandatory checking of document details fields in the mobile terminal  
 [Fixed] Fix the problem of mobile login jumping  
 [Fixed] Repair the problem that the customized document status does not take effect  


## [Version: 2.6.7] - 2023-08-22
 [Improved]Show pop-up window when you don't have permission to view documents.  
 [Improved] Change the adopted English to Agree when editing the English of approval nodes to maintain consistency.     
 [Improved] Add a new switch for daily notification of document handling.  
 [Improved] Error message when attachment is abnormal  
 [Improved]Error message when third-party api return protocol is not satisfied.  
 [Improved] Modify account number to account number  
 [Fixed] Fix the problem that custom document status is not effective.

## [Version: 2.6.6] - 2023-07-13
 [Improved] Internationalization content supplement  
 [Fixed] Fix the problem that the public field is configured with the API data source that the data cannot be displayed after the data source cannot be displayed    
 [Fixed] Repair the document page service directory is not related to the project associated with the project  
 [Fixed] Repair the service batch deletion of the directory after the directory deletes failure  
 [Fixed] Data statistical table sorting conditions have not taken effect, repair the problem  
 [Fixed] Project field form update time By ranks incorrect problems repair  
 [Fixed] The list of repair documents is empty as the form is not correct  
 [Fixed] The problem that the trigger processor cannot choose the second level drop -down box when choosing the role of the permissions center  
 [Fixed] Repair the problem of calling the right of the center interface when the switch language is repaired  
 [Fixed] Modify the list interface of the document list interface  
 [Fixed] Priority release user custom restrictions  
 [Fixed] Fix bugs that fail to flow in documents due to the token conflict  
 [Improved] Automatically adjust the single time to 5s  
 [Fixed] When repairing the approval person is too much, the user prompts the problem that there is no authority  
 [Fixed] Fix the problem of abnormal exit when the API node MESSAGE returns the dictionary  
 [Fixed] The issue of the attachment path of the system under the containerized environment  
 [Fixed] Fix the problem that the custom state that cannot be empty cannot be empty   

## [Version: 2.6.5] - 2023-05-11
 [Improved] Support CDN solution  
 [Improved] Internationalization content supplement  
 [Improved] Optimize the interaction effects of batch approval

## [Version: 2.6.4] - 2023-04-07
 [Fixed] Modify the style of the document urging and basic information, repair the custom form editing display 
 [Improved] Modify the leakage urging copywriting  
 [Improved] Newly add OpenAPI interface to quickly obtain the approval results of an approval node  
 [Fixed] Modify the table air data status and text overflow display TIPS  
 [Fixed] Fix the text overflowing the empty state omissions  
 [Improved] Approval document adding project ID filtration  
 [Improved] Optimized when there are too many documents, the loading speed of my approval list  
 [Improved] Optimize the list of request project lists 

## [Version: 2.6.1] - 2022-03-31
 [Feature] Community edition does not open the Blue Shield node         
 [Feature] Popover problem fixed, development framework version updated             
 [Improved] Abnormal statistics of approval number after order transfer            
 [Feature] Notification template for project latitude         
 [Improved] Update the permission model                   
 [Fixed] Sending orders to the organization structure is abnormal          
 [Fixed] Work order view permission authentication exception repair         
 [Feature] Support automatic node exception notification        
 [Feature] Custom tabs within the project         
 [Feature] Global trigger within a project        
 [Feature] Merge service and service catalog     
 [Feature] Services support cloning     
 [Feature] Commentary on documents

## [Version: 2.6.0] - 2021-09-09
 [Feature] Project Space, each project space manages the documents, services, elements, SLAs, and configuration management under the project.  
 [Feature] Platform Management, manage the basic/public configuration at platform level  
 [Improved] Merge service and process concepts, eliminate process version  
 [Improved]Front-end UI design optimization  
 [Improved] Permission model update  
 [Fixed] Assignment of orders to organizational structure exceptions
 [Fixed] When creating a service, the service bill of lading information is not selected  
 [Improved] Add fields, custom data duplication data correction still prompts duplication  
 [Improved] Hide content related to the knowledge base  
 [Improved] The newly created user is transferred to the general role, the user group cannot be pulled, and there is no prompt to apply for permission  
 [Improved] Notification configuration permission settings, those without permission should be grayed out + locked  
 [Improved] No prompt for user group delete permission  
 [Improved] Edit the existing fields of the service bill of lading information, which cannot be saved  

## [Version: 2.5.9]-2021-05-07
 [Fixed] Failed to download file in attachment upload field  
 [Fixed] Repair the standard operation and maintenance form reference variable is edited again, the checked state is lost  
 [Fixed] Abnormal field display when creating a task  
 [Fixed] Some standard operation and maintenance tasks click to handle/view and report an exception  
 [Fixed] The remaining time of sla in the current step increases  
 [Fixed] New service agreement cannot be submitted & fixed my ticket to-do tab number is occasionally displayed incorrectly  
 [Fixed] After repairing the basic information of the editing service, it is not updated  
 [Improved] Trigger conditions for initializing the community version of the Blue Shield mission template  
 [Improved] Added an exception when the standard operation and maintenance interface reports an error  
 [Fixed] 2.5.8 Upgrade 2.5.9 will cause upgrade failure  
 [Fixed] Abnormal field display when creating a task  
 [Fixed] Some standard operation and maintenance tasks click to handle/view and report an exception  
 [Fixed] The remaining time of sla in the current step increases  
 [Fixed] New service agreement cannot be submitted & fixed my ticket to-do tab number is occasionally displayed incorrectly  
 [Fixed] After repairing the basic information of the editing service, it is not updated  
 [Improved] Trigger conditions for initializing the community version of the Blue Shield mission template  
 [Improved] Added an exception when the standard operation and maintenance interface reports an error  
 [Feature] The receipt supports multi-node and multi-task mode  
 [Feature] Standard operation and maintenance tasks can reference variable functions  
 [Feature] Functional support for segmented SLA  
 [Feature] Supports tasks in multi-node  
 [Feature] Supports to reference variable for SOPS task  
 [Feature] New version of SLA  

## [Version: 2.5.8] - 2021-03-16
 [Feature] New version of operational data released  
 [Feature] Exception handling when the person is empty  
 [Feature] SOPS release scenarios support replenishment orders  
 [Improved] List query speed optimization  
 [Improved] Organizational structure personnel display optimization  
 [Improved] Export logic optimization  
 [Fixed] Handler issues when dispatching and transferring orders  
 [Fixed] Inaccurate display of my to-do content  
 
## [Version: 2.5.7] - 2020-12-30
 [Feature] SOPS release scenario support  
 [Feature] IAM approval scenario support  
 [Feature] redis sentinel double password  
 [Feature] Ticket front page reconstruction and revision  
 [Feature] Ticket detail reconstruction and revision  
 [Feature] International integration of front and backend  
 [Feature] Add IAM built-in approval process  
 [Feature] Improved of the withdrawn strategy logic, support users to configure withdrawn rules  
 [Feature] The role of the processor is increased to specify the superiors of different people  
 [Feature] Add trigger record display tab for ticket details  
 [Fixed] Product document jump to document center  
 [Fixed] Add built-in workflow and services  
 [Fixed] Get service role is compatible with the scenario of not creator  
 [Fixed] pipeline add candidate backend  
 [Fixed] Add visible range configuration for API docking  
 [Fixed] Title distinguish Enterprise Edition Community Edition  
 [Fixed] Help add product documentation and problem feedback  
 [Fixed] Product document jump to document center  
 [Fixed] Attention ticket authentication logic  
 [Improved] Moa application content optimization  
 [Improved] Many errors were reported at 401  
 [Improved] Report IAM changed to internal PAAS address  
 [Fixed] Enterprise WeChat bots send multi messages when they are too large  
 [Fixed] Flow details interface error, and the extra field exceeds the limit  
 [Fixed] Service details interface permission issue  
 [Fixed] Inactive services appear at the service entrance  
 [Fixed] Custom table data is not backfilled  
 [Fixed] Required fields of custom form are not verified  
 [Fixed] Unable to unlink order
 [Fixed] Repair the homepage waiting for my approval number is not refreshed  
 [Fixed] The page freezes when the processor organization structure  
 [Fixed] handle abnormal standard operation and maintenance tasks  
 [Improved] member synchronization mechanism of CMDB role  
 [Improved] export function optimization  
 [Fixed] line trigger cannot be triggered  
 [Fixed] access to role members
 [Fixed] the task handler of the execution node cannot see the document  
 [Fixed] no problem found in node clone field  
 [Fixed] invalid deletion of nodes  
 [Improved] select the service and export the ticket according to the service bill of lading field  
 [Feature] log retrieval process initialization deployment  
 [Fixed] fix the problem of alarm sending failure because the function name cannot be obtained from the stack  
 [Fixed] the business card will not be displayed  
 [Improved] case support for service search  
 [Fixed] The details of the repair node are not displayed in the current step  

## [Version: 2.5.6] - 2020-10-22
 [Feature] Process configuration adds support for IAM roles  
 [Feature] Caching supports RedIS configuration  
 [Feature] Support for IAM instance search  
 [Feature] Add department information to business CARDS  

## [Version: 2.5.5] - 2020-09-26
 [Feature] Process configuration add support authority center role  
 [Improved] New version of personnel component replacement  
 [Improved] Basic configuration removes organizational structure switch  
 [Fixed] Migrate reports an error when deployed separately  
 [Fixed] Process service name modification  
 [Fixed] Selection of cross-domain personnel  
 [Fixed] IAM request link uses BK_PAAS_INNER_HOST by default  

## [Version: 2.5.4] - 2020-09-07
 [Feature] Add permission upgrade of version 2.4  
 [Feature] Add built-in approval process  
 [Feature] Process configuration add support authority center role  
 [Improved] Bill of lading field verification prompt optimization  
 [Improved] The name of the follower and the follower are conflicted, and the follower is modified to an email notification  
 [Improved] All Ticket in the list of Tickets are released, everyone can see  
 [Fixed] Fixed the bug that the built-in approval process failed to initialize  
 [Fixed] Add view button in task table to view the task details   
 [Fixed] When submitting the document, the dirty data of the previous node will be transferred to the current operating node  
 [Fixed] The style of the workbench is messy after zooming  
 [Fixed] Incomplete display of current processing steps  
 [Fixed] The  sops template cannot be seen if no business is selected  
 [Fixed] Remove the automatic execution content from statistical data  
 [Fixed] The front-end style still shows that it has been followed after failing to follow the receipt  
 [Fixed]  Back to the homepage is invalid when the user close the last tab  
 [Fixed]  The creator actions granting will not be performed if the creator does not exist  
 [Fixed]  The content after the api request parameter will overwrite the previous content  
 [Fixed]  The current step is not updated after dispatch  
 [Fixed]  The operation node cannot check the recurrence box again and cannot submit  
 [Fixed]  The rich text control is upgraded to solve minor problems such as invalid bolding  
 [Fixed]  The api log information name and processing time are not displayed  
 
## [Version: 2.5.3] - 2020-09-01
 [Fixed] When previewing the flowchart, it prompts no permission problem fixed  
 [Fixed] The new task page is not rendered, and an error is reported in the console  
 [Fixed] The front end style is still displayed after the note fails  
 [Fixed] When there is only one nav in the ticket details, delete no response  
 [Improved] Missing prompt for service list deletion  

## [Version: 2.5.2] - 2020-08-20
 [Feature] Add approval node
 [Feature] New field default value to add rich text  
 [Feature] Api node failure processing (retry, ignore)  
 [Feature] Add batch approval
 [Feature] Add followers
 [Improved] If the status of the countersignature node or the approval node is in process, the submit button will display loading  
 [Improved] After the workbench express bill of lading is completed, it will default to the global list of "all bill"  
 [Improved] The processor component is changed to display one line when out of focus, and multiple lines when in focus  
 [Improved] Quick bill of lading jump to the global view My application form  
 [Improved] Work order list and work order detail style optimization  
 [Improved] The pass platform application permission will open in a new browser tab  
 [Improved] After the permission application is passed, the menu bar refreshes without updating the permissions  
 [Fixed] Fix the bug which raise exception "schedule service does not exist" when operate task.  
 [Fixed] Fix displaying error of component type  
 [Fixed] New field default value to add rich text  
 [Fixed] Follow people button, follow people list  
 [Fixed] The existing sequence is restored after adding new fields to the process design field list  
 [Fixed] Fix the current step of the bill list is empty  
 [Fixed] Fix log details only show the last one  
 [Fixed] When the process administrator, the process design menu is not displayed  
 [Fixed] Fix llog details handler field error  

## [Version: 2.5.1] - 2020-07-31
 [Feature] Support to register auth action groups  
 [Feature] Support to grant related actions's permission after resource created  

## [Version: 2.5.0] - 2020-07-02
 [Feature] System authentication depends on IAM  
 [Improved] Icon migrate to iconcool  
 [Improved] Replaced task icon  
 [Improved] Global view table optimization, add processor, filter conditions, custom table header, etc.; i18n extraction  
 [Improved] The time control displays the current time by default  
 [Improved] Background management menu icon replacement  
 [Fixed] Global view current processors error  
 [Fixed] Pass platform cannot open permission center  
 [Fixed] Cannot submit with default hidden fields  
 [Fixed] Fix permissions for process design deployment  
 [Fixed] Fix the new creation of sla service agreement management, turn off the reminder mechanism, there is still verification  
 [Fixed] Fix /role/users api has no role_type parameter  
 [Fixed] Fix the blinking of ticket details  

## [Version: 2.4.2] - 2020-05-26
 [Feature] Task-group is supported  
 [Feature] Support task group function in the process  
 [Feature] node configuration remove action button  
 [Feature] Trigger configuration management  
 [Feature] Support trigger function in the process  
 [Feature] Support configuration management of process administrator and person in charge  
 [Feature] API supports writing sandbox code  
 [Feature] Expansion of public variables in the process  
 [Feature] System function switch  
 [Feature] Provide fast bill entrance  
 [Fixed] Fix the defect of rich text packaging  

## [Version: 2.4.4] - 2020-08-10
 [Feature] New field default value to add rich text  
 [Feature] Api node failure processing (retry, ignore)  
 [Feature] Add batch approval
 [Feature] Add followers
 [Feature] Links in rich text support opening in new tabs  
 [Improved] If the status of the countersignature node or the approval node is in process, the submit button will display loading  
 [Improved] The processor component is changed to display one line when out of focus, and multiple lines when in focus  
 [Improved] Quick bill of lading jump to the global view My application form  
 [Improved] Work order list and work order detail style optimization  
 [Improved] Magicbox upgraded to 2.2.1  
 [Improved] Node details and log details style optimization  
 [Fixed] Fix the bug which raise exception "schedule service does not exist" when operate task.  
 [Fixed] Fix displaying  error of component type  
 [Fixed] New field default value to add rich text  
 [Fixed] Follow people button, follow people list  
 [Fixed] The existing sequence is restored after adding new fields to the process design field list  
 [Fixed] Fix the current step of the bill list is empty  
 [Fixed] Fix log details only show the last one  
 [Fixed] When the process administrator, the process design menu is not displayed  
 [Fixed] Fix llog details handler field error  
 [Fixed] After the approval node is processed, the current step interface is not updated after polling  
 [Fixed] Fix Sops node details task parameters are not displayed  
 [Fixed] A default value will be matched when the person selector is empty  

## [Version: 2.4.3]-2020-07-10
 [Feature] Add new trigger action that to send messages by group robot  
 [Feature] Add line display in document flow chart view   
 [Improved] Add skip exclusive node for error configuration  
 [Fixed] Fix the new creation of sla service agreement management, turn off the reminder mechanism, there is still verification  
 [Fixed] Fix /role/users api has no role_type parameter  
 [Fixed] Fix the blinking of ticket details  
 [Fixed] Template filling will clear the fields that are not in the current field list  
 [Improved] Get all users information before serialize tickets' data  
 [Improved] The expanded display details of the log list are changed to the side-sliding pop-up window display  

## [Version: 2.4.2]-2020-05-26
 [Feature] Task template configuration management  
 [Feature] Support task group in the ticket  
 [Feature] Remove action button configuration in node  
 [Feature] Trigger configuration management  
 [Feature] Support trigger function in the process  
 [Feature] Add permission settings in flow design  
 [Feature] API supports writing sandbox code  
 [Feature] Expansion of public variables in the process  
 [Feature] Add new system function switch  
 [Feature] Provide fast bill of lading entrance  
 [Fixed] Fix the defect of rich text packaging  

## [Version: 2.4.1] -2020-03-11
 [Feature] Front-end component upgrade  
 [Feature] Officials support the configuration of dynamic handlers  
 [Improved] Official support for configuring action buttons  
 [Feature] Baseline supports association constraints  
 [Improved] Support staff configuration organization structure (dependency: open_paas_ee> = 2.10.26, usermgr_ee> = 2.0.5)  
 [Fixed] Chinese name process caused garbled characters  

## [Version: 2.3.1] -2019-12-27
 [Improved] SLA management module  
 [Improved] Basic model and public interest  
 [Improved] Sort service catalog  
 [Improved] Radio Selector Component  
 [Feature] Notification template open configuration  
 [Improved] Internationalization  
 [Improved] single function of mother and child  
 [Improved] Upgrade development framework  
 [Improved] Upgrade to Python3  
 [Improved] Open preset key editing  
 [Improved] The document withdrawal function can be switched  
 [Improved] Process preview function can be switched  
 [Improved] Provide catalog view  
 [Improved] single number differentiated service  
 [Improved] Operation data query optimization  
 [Data migration] To transfer configuration related data, you need to run http://{host}/helper/db_fix_after_2_3_1/  

## [Version: 2.2.22] - 2020-03-21
 [Feature] support self-service apis  
 [Fixed] fix api node save bugs  

## [Version: 2.2.21] - 2020-03-03
 [Feature] add english version logs  
 [Feature] playing the login window function  
 [Fixed] process of Chinese export problem  
 [Fixed] some translation problems  
 [Fixed] some translation problems  

## [Version: 2.2.20] - 2020-01-20
 [Fixed] repair field repair API process caused by the import problem  

## [Version: 2.2.19] - 2020-01-16
 [Fixed] international various translation problems  
 [Fixed] to do show incorrect repair problem  

## [Version: 2.2.18] - 2020-01-08
 [Feature] custom deployment template  
 [Feature] documents concerned notifications  
 [Improved] Improved of standard operational node error display  
 [Fixed] test its repair failure problem  
 [Fixed] create correlation problem of the single failure repair  
 [Fixed] 2.2.17 front-end bug fixes  
 [Fixed] interface to turn single person authentication error problem of repair operation  
 [Fixed] interface to get repair service list problem  

## [Version: 2.2.17] - 2019-12-18
 [Improved] Optimal replacement personnel selector  
 [Improved] optimization documents list query logic  
 [Improved] the optimization of the bill of lading interface  
 [Feature] to do little red dot  
 [Feature] field default values  
 [Feature] provide English description information  
 [data migration] new documents list query logic, need to be run as an administrator http://{host}/helper/db_fix_after_2_2_17/  

## [Version: 2.2.16] - 2019-12-10
 [Fixed] fix its problem  

## [Version: 2.2.15] - 2019-12-06
 [Feature] support custom deployment template  
 [Fixed] repair admin page selection function  
 [Fixed] gm role the administrator role table click no response management problems  
 [Fixed] concurrent bill of lading, single number repeated problems  
 [Fixed] standard operational node hop link problem  
 [Fixed] translation problems  

## [Version: 2.2.12] - 2019-11-19
 [Fixed] repair admin page selection function  

## [Version: 2.2.11] - 2019-11-08
 [Feature] tag support new node  
 [Feature] provide documents processing interface  
 [Feature] provide node processing interface  
 [Improved] documents log interfaces and status  
 [Improved] documents hangs, restore and suspension  
 [Fixed] international translation problems  
 [Fixed] process engine deadlock problem  

## [Version: 2.2.9] - 2019-11-05
 [Feature] nodes replication  
 [Feature] sorting services, service directory  
 [Fixed] repair documents translation problems  
 [Fixed] fix API log growing too fast  
 [Fixed] repair documents revoked display problems  
 [data migration] attachment storage upgrade need to run as an administrator http://{host}/helper/db_fix_for_attachments/  

## [Version: 2.2.8] - 2019-10-29
 [Fixed] repair work order statistics administrator privileges  
 [Fixed] repair ordinary users to look at front nodes problem  
 [Fixed] repair notice problems  
 [Fixed] repair accessories problems  
 [Fixed] repair bill of lading HouGong single filtering problem  
 [Fixed] fix its problems  
 [Improved] optimization documents processing  
 [Improved] the optimization of the bill loading  

## [Version: 2.2.7] - 2019-10-25
 [Fixed] repair log style  
 [Fixed] The attachment/repair repair data migration   
 [Fixed] repair invited evaluation function  

## [Version: 2.2.6] - 2019-10-23
 [Feature] can set the environment variable closed notification function: BKAPP_CLOSE_NOTIFY = 'close' the closure notice  
 [Fixed] repair enterprise WeChat data dictionary  
 [Fixed] repair enterprises WeChat hidden field problems  
 [Fixed] repair workbench/operational data chart  
 [Improved] Operation documents page display  
 [Improved] Logical/style/optimization associated documents  

## [Version: 2.2.3] - 2019-10-16
 [Feature] open API interface  
 [Fixed] repair data migration issues  
 [Fixed] Drop-down box/repair repair custom form style  
 [Fixed] fix international translation problems  
 [Fixed] repair print issue  
 [Fixed] repair work order export problem  
 [Fixed] repair enterprise WeChat problem  

## [Version: 2.2.1] - 2019-08-22
 [Feature] process engine upgrades, support rule configuration, branch, parallel features such as flexible support, support conditions of complex configuration process lines  
 [Feature] process elements increases the API node, standard operational procedure, supporting configuration process automation  
 [Feature] API management functions, support API access gateway system and configuration details of the interface protocols  
 [Feature] API fields, show the list of the third party system data support  
 [Feature] version log viewer  
 [Feature] open to the public API, built single/check list, etc  
 [Feature] database upgrade function  
 [Improved] process editor interactive upgrade, support drag define the process  
 [Improved] optimize enterprise edition accessories directory configuration optimization  
 [Improved] documents related to the optimization and adjustment of the page  
 [Improved] upgrade Django version to 1.11.23  
 [Improved] documents details page preview support process and details view  
 [Improved] the current version temporarily removed for examination and approval of mobile terminal function  
 [data migration] the process version, services such as data upgrade: http://{host}/helper/db_fix_from_2_1_x_to_2_2_1/  

## [Version: 2.1.17] - 2019-08-16
 [Feature] service scope of visible function (support structure radio)  
 [Feature] support services more search criteria  
 [Feature] service items associated with process version features: association/unbundling  
 [Feature] process versioning: reduction, preview, delete  
 [Feature] process design management field type  
 [Feature] tree field  
 [Feature] processing process design management role can be pulled from the organizational structure of choice  
 [Feature] process design can choose complex form components  
 [Feature] process design judgment node can be back  
 [Feature] flow field support for the data dictionary  
 [Feature] data dictionary management and application  
 [Feature] data dictionary in the application of the process design  
 [Feature] attached storage configuration  
 [Feature] cache configuration  
 [Feature] organizational function switch  
 [Feature] merger management page  
 [Feature] SLA management function is applied to all services  
 [Feature] enterprise WeChat application version  
 [Feature] documents supervisory functions  
 [Feature] process preview function  
 [Feature] notice attention function  
 [Feature] complex form fields  
 [Feature] judgment nodes support back  
 [Feature] increase release and deployment management portal  
 [Feature] increase fast and the bill of lading entry  
 [Feature] organizational information display  
 [Feature] service classification collection function  
 [Feature] add attachments directory configuration function  
 [Feature] operating data view online  
 [Feature] according to the process id of the repair order interface, query process list interface  
 [Feature] field support for regular check  
 [Feature] enterprise WeChat inform support sending messages to a specific application  
 [Feature] work order status increase with dispatch/with claim  
 [Feature] ITSM administrator role, supporting the view and manage all documents  
 [Feature] support third party bill of lading operation system after login  
 [Improved] To optimize the field calibration problem  
 [Improved] Cascade query optimization business  
 [Improved] Optimize the page refresh optimization  
 [Improved] number length adjustment  
 [Improved] "Improved" according to Chinese user name  
 [Improved] Change the default notification template  
 [Improved] Query interface optimization optimization documents  
 [Improved] data dictionary form the export  
 [Improved] Improved of multistage display tree structure data dictionary  
 [Improved] filter documents to support the parent service directory  
 [Improved] For the bill of lading/optimization process versioning of logic and adjustment  
 [Improved] accessories store directory configuration optimization (docs/itsm_nfs)  
 [Improved] Improved service items, service directory to upgrade the original classification management  
 [Improved] CMDB caching policy adjustment and support to clear the cache  
 [Improved] with plug-in replacement echarts plotly chart  
 [Improved] documents form displays details page optimization  
 [Improved] Improved dispatch function to strengthen, support assignment in groups  
 [Improved] Optimize upgrade page interaction, support side up  
 [Improved] Optimizing adjustment documents sorting, sort by creation time  
 [Improved] Overall optimization page revised documents (query, view, processing, etc.)  
 [Improved] Optimize upgrade time controls, support more editing functions  
 [Improved] Improved of adjusting part of the form controls, support multiple queries  
 [Improved] all document flow operation increase secondary pop-up window to confirm  
 [Fixed] templates save problem  
 [Fixed] Repair/repair security problem  
 [Fixed] Preview/repair process problems  
 [Fixed] General character creation problem  
 [Fixed] work order dispatch failure problem  
 [Fixed] Preview version problem/repair process  
 [Fixed] repair process import format problem  
 [Fixed] Couldn't query the problem for dispatch  
 [Fixed] Personal display/repair process people  
 [Fixed] event classification query failure problem  
 [Fixed] Pack up node does not fill out the problem  
 [Fixed] The role of CMDB can not bill of lading  
 [Fixed] state of countless according to operational data  
 [Fixed] template box does not cover problem  
 [Fixed] about changes in the knowledge base to upload attachments  
 [Fixed] work order SLA/derived form numerous according to the problem  
 [Fixed] dispatch documents without permission to claim problem  
 [Fixed] Repair the custom form to print, mobile terminal display problems  
 [Fixed] the bill of lading can not to choose operation character of the nodes  
 [Fixed] After CMDB3.2.6 version cascade field failure problem  
 [Fixed] change flow field type, lead to the repair order template error problems  
 [Fixed] repair template/draft/work order caused by dirty data security issues  
 [Fixed] repair claim work order response time for computational problems  
 [Fixed] repair parts has finished the repair order not calculated over a matter of time  
 [Fixed] changes in both Chinese and English name is stored  
 [Fixed] repair work order title data problems  
 [Fixed] repair work order log data  
 [data migration] V1.1. X to V2.1. X data upgrade interface (suggested data backup in advance) : http://{host}/helper/db_fix_from_1_1_22_to_2_1_16/  

## [Version: 1.1.22] - 2018-11-27
 [Feature] global view  
 [Feature] knowledge base function module  
 [Feature] request management module  
 [Feature] problem management module  
 [Feature] documents printing function  
 [Feature] documents directly evaluation function  
 [Feature] form field support for regular check  
 [Feature] messages inviting evaluation function  
 [Feature] documents claim, the dispatch function  
 [Feature] work order bill of lading template  
 [Feature] increases the title field  
 [Feature] new query historical documents  
 [Feature] work order statistics administrator role  
 [Feature] new suspend and resume function  
 [Feature] process support configuration focuses on people  
 [Feature] work order support hangs, restore and revocation  
 [Feature] documents processing process, support save drafts  
 [Feature] username support Chinese display  
 [Feature] judgment types support configuration form and termination of the operation  
 [Feature] increase super administrators and built a single undo function of documents  
 [Feature] add flow log operator, documents of the bill of lading user name support Chinese display  
 [Feature] export documents, contains all the information field  
 [Feature] to turn single turn single reason need to fill in  
 [Feature] After the back to keep the latest operation information  
 [Improved] Optimize the homepage function changes  
 [Improved] Show/optimization of the bill of lading entry optimization, process and instructions  
 [Improved] To optimize the export function optimization, process sheet  
 [Improved] documents, query optimization, selection of the bill of lading query  
 [Improved] optimization dispatching and claimed function optimization  
 [Improved] Improved of the bill of lading service directory to choose, only show the directory associated with the service process  
 [Improved] according to the process of the module name when creating documents to build single choice  
 [Improved] judgment node and ordinary node can add fields, can be terminated  
 [Improved] cancel resource application management module (classified to request management)  
 [Improved] documents sent notice to distinguish the attention and the processing  
 [Improved] Improved process log order adjustment, displayed in chronological order  
 [Improved] Improved in the process of editing, there is no limit to the property  
 [Fixed] non-administrative abnormal issues fixed page open access list  
 [Fixed] the trouble of bill of lading caton processing  
 [Fixed] user query less than Chinese revised documents  
 [Fixed] knowledge base function module repair style question  
 [Fixed] documents print numerous repair according to the problem  
 [Fixed] send notification after deleted field repair error problem  
 [Fixed] to keep the time of flow field in the business field is empty problem to repair  
 [Fixed] Get the role list there is no exception for incorrect repair problem  
 [Fixed] failure event when acquiring the related business is empty repair times wrong problem  

## [Version: 1.1.3] - 2018-09-18
[Feature] support end operation  
[Feature] support attachments upload template  
[Feature] allows you to set single range  
[Feature] change management, fault event management, resource application, inventory management, role management, process design  
[Feature] rejected and termination of operations must be fill in  
[Feature] compatible with HTTPS  
[Improved] Optimize the process, main process between connected by arrows  
[Improved] Optimize the validation rules to update  
[Improved] Optimize the optimization send SMS  
[Fixed] Other issues fixed  
[Fixed] non-administrative single permission problems  
[Fixed] part of the space name lookup  
[Fixed] because of the lack of new change processes in change type lead to failure  
[Fixed] upload_file upload 403 bug fixes  
[Improved] the attachment function ` NFS mount ` catalogue, hang under the path to the root directory of ` USERRES `  
[Improved] suggest ` mysql > = 5.7 `, currently compatible with 5.6 ` `, subsequent versions consider upgrading to 5.7 ` `  
