
&nbsp;
**Key Takeways - TL;DR - GenAI leverages AI and Microservice Automation for 'hands-free' project creation**
&nbsp;

    API Logic Server uses ChatGPT APIs, to submit prompts and obtain data model class responses.  
    
    API Logic Server uses these to create a database and project, from a single `genai` command.

    This document illustrates how to create, run and customize the genai_demo project.

    > Note: if you have already created the project, proceed to "What Just Happened?".

&nbsp;

[![GenAI Automation](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/genai-automation-video.png?raw=true)](https://www.youtube.com/watch?v=LSh7mqGiT0k&t=5s "Microservice Automation")

&nbsp;

## 1. Description (or Database)

To create a microservice, identify an existing database, or provide a natural language "prompt" description.  For example, here is the `genai_demo.prompt` file:


&nbsp;
**Key Takeways - TL;DR - GenAI Prompt**
&nbsp;

    Create a system with customers, orders, items and products.

    Include a notes field for orders.

    Enforce the Check Credit requirement (do not generate check constraints):
    
    1. Customer.balance <= credit_limit
    2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
    3. Order.amount_total = Sum(Item.amount)
    4. Item.amount = quantity * unit_price
    5. Store the Item.unit_price as a copy from Product.unit_price

&nbsp;

## 2. GenAI Creation

You can explore genai_demo using the [Manager](https://apilogicserver.github.io/Docs/Manager/).  Optionally, you can sign-up for ChatGPT API and Copilot, or simulate the process as described below.

1. If you have signed up for ChatGPT API and Copilot, this command will create and open a project called `genai_demo` from `genai_demo.prompt`:

```bash
als genai --using=genai_demo.prompt
```


2. ***Or,*** if you have not signed up, you can simulate the process using a pre-installed response file:

```bash
als genai --using=genai_demo.prompt --gen-using-file=system/genai/temp/chatgpt_retry.txt
```

&nbsp;

### What Just Happened?

`genai` processing is shown below (internal steps denoted in grey):

1. You create your.prompt file, and invoke `als genai --using=your.prompt`.  genai then creates your database and project as follows:

    a. Submits your prompt to the `ChatGPT API`

    b. Writes the response to file, so you can correct and retry if anything goes wrong

    c. Extracts model.py from the response

    d. Invokes `als create-from-model`, which creates the database and your project

2. Your created project is opened in your IDE, ready to execute and customize

&nbsp;

![Microservice Automation](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/genai.png?raw=true)

&nbsp;

### API/App Automation

API/App Automation means the created project is executable.  To run:

1. Press **F5** to run
2. Start your [Browser](http://localhost:5656/) to view:
    * App Automation: the Admin App, and
    * API Automation: JSON:API, with Swagger
3. Stop the server when you are done (red box on VSCode Debugger panel)

![Microservice Automation](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/Microservice-Automation.png?raw=true)

It's a modern, 3-tiered architecture, using standard Python libraries:

![Microservice Architecture](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/Architecture-Runtime-Stack.png?raw=true)

&nbsp;

## 3. Customize: Rules and Python

The development environment is also standard: your IDE, standard languages, standard libraries, standard source control, etc.  You customize API Logic Project in two ways, both performed in your IDE:

* **Logic Automation:** declare spreadsheet-like rules to address multi-table derivations and constraints.  These constitute nearly half of a typical database-oriented system.   Declarative rules are 40X more concise than procedural code.

* **Standard Python:** e.g, to create a new custom endpoint, and send a Kafka message

Explore these below.

&nbsp;

### Logic Automation

To explore rules:

1. Open `logic/declare_logic.py`

2. Copy the comments to your Copilot window, starting with the line with **GenAI:**

3. Paste them into the Copilot Chat windows

4. Paste the generated code back into `logic/declare_logic.py`.  You will need to make a few small repairs:

    * change *import models* to *import database.models*, and 
    * change *as_formula* to *as_expression*

![Add Rules](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/add-rules.png?raw=true)

&nbsp;

### Standard Python, Libraries

To save time, issue the follow command to simulate changes you might make in your IDE, e.g., to create a new custom endpoint, and send a Kafka message.

```bash title="Simulate IDE Customization"
als genai-cust
```

![Customize](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/genai_cust.png?raw=true)

### Try it out

Set a breakpoint in the code above, and:

1. Start the Server (**F5**)
2. Use the Admin app to alter the first Customer, first Order, first Item, and change the quantity to 11111
    * Observe the error message, from the rules.
3. To test the new endpoint, use Swagger (**ServicesEndPoint > POST /ServicesEndPoint/OrderB2B)**.
    * Observe the swagger response - "Sending Order to Shipping sends:".

Note: Kafka is not activated in this example.  To explore a running Tutorial for application integration with running Kafka, [click here](Sample-Integration.md).

&nbsp;

## 4. Deployment: Containers, Cloud

One of the best ways to de-risk projects is to verify the sponsors are in sync with what is happening.  This is best addressed with *working software*, which often occurs late in project development.  Surprises here can result in considerable rework... and frustrations.

GenAI Automation produces *working software, now*, so you can find misunderstandings before investing serious effort ("fail fast").  To expose the working software, it's often desirable to deploy to the cloud so business users can run it.

API Logic Server creates the `devops` directory, which scripts to containerize your project, and deploy it to Azure.  For more information, see [DevOps Automation](https://apilogicserver.github.io/Docs/DevOps-Automation/).

&nbsp;

## Appendices

&nbsp;

### GenAI Restart Procedures

AI results are not consistent, so the created model file may need corrections.  You can find it at `system/genai/temp/model.py`.  You can correct the model file, and then run:

```bash
als create --project-name=genai_demo --from-model=system/genai/temp/model.py --db-url=sqlite
```

Or, correct the chatgpt response, and

```bash
als genai --using=genai_demo.prompt --gen-using-file=system/genai/temp/chatgpt_retry.txt
```

&nbsp;

CLI Notes (effective as of release 11.00.22):

* Projects are created in the your current working folder (typically the manager root directory).  They were formerly created adjacent to the `gen-using-file`.

* The project name is the last node of `--using`.  This is a required argument, since it denotes the project directory name.

We have seen failures such as:

* duplicate definition of `DECIMAL` (we hand-fix the response to fix this)
* unclosed parentheses
* data type errors in test data creation
* wrong engine import: from logic_bank import Engine, constraint
* bad test data creation: with Engine() as engine...
* Bad load code (no session)
* missing datetime import
* relationship property errors ("mapper has no property...")

&nbsp;

#### Diagnosis Tips

The system saves files used for creation: 

![Customize](https://github.com/ApiLogicServer/Docs/blob/main/docs/images/sample-ai/copilot/diagnostic_info.png?raw=true)

Note there are multiple diagostic directories.  recall GenAI results are not always predictable, so we make 3 attempts to get a successful result.  This is often enough, but examining the failures can be useful.

A good technique is to:

1. **Open the response file in the Manager**, and
2. Use your IDE to run the file 

It's usage create the sqlite database, but running it in this mode can provide more insight into causes.

If you are using [Web/GenAI](WebGenAI.md), project files are always under /projects/gen_$ID.

&nbsp;

### GenAI Using Postgresql

The above examples use *sqlite,* since it requires no install.  The GenAI process works for other database, such as Postgresql.

You can test this as follows:

1. Use [our docker image](https://apilogicserver.github.io/Docs/Database-Docker/)
2. And:

```bash
als create --project-name=genai_demo_pg.prompt --db-url=postgresql://postgres:p@localhost/genai_demo
```

Provisos:

* You have to create the database first

