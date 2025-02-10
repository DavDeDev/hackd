
# Next.js & GitHub Actions

[![1-click-deploy](https://defang.io/deploy-with-defang.png)](https://portal.defang.dev/redirect?url=https%3A%2F%2Fgithub.com%2Fnew%3Ftemplate_name%3Dsample-nextjs-github-actions-template%26template_owner%3DDefangSamples)

A basic Next.js app with a Dockerfile and docker-compose ready to deploy to AWS with [Defang](https://defang.io) with GitHub Actions configured for CI/CD.

## Steps to Set Up 

1. **Install Defang**  
   Run the following command to install Defang:
   ```
   brew install DefangLabs/defang/defang
   ```

2. **Authenticate with Defang**  
   After installation, authenticate by running:
   ```
   defang login
   ```

   Follow the on-screen instructions and open the provided URL to complete authentication.

3. **Optional: Authenticate with AWS**  
   To authenticate with AWS, follow [this guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html).

4. **Set Up Environment Variables**  
   Copy the `.env.local.template` file and rename it to `.env.local`. Then fill the environment variables with the required values.

5. **Set up Authentication**
   To setup Convex authentication, follow the steps in [this tutorial](https://labs.convex.dev/auth/config/oauth)
   From this, you would get the necessary variables to fill up what is needed as indicated in the .env template. 

5. **Navigate to the Web Directory**  
    To ensure you're in the right project directory where the Next.js app is located, move to the `web` folder by running the command:
    ```
    cd web
    ```
    This step is important as it ensures you're in the correct location to install project dependencies in the next step.


6. **Install Dependencies**  
   Install all required dependencies by running:
   ```
   npm install
   npm install @radix-ui/react-label
   ```

7. **Run the Application**  
   Before doing npm run dev, you show make sure that the email your github is associated with, has been added as an Admin in the convex Member tab. 
   Start the application by navigating to the project root and running:
   ```
   npm run dev
   ```
   Select choose an existing project, pick the right team, pick yes when it comes to the right project, and you are good.

   If there are issues with missing configurations, ensure the `.env.local` file is set correctly and run `defang config` to manage sensitive configs.

8. **Defang Docker Compose Up**  
   Run the following command to start the Docker container:
   ```
   defang compose up
   ```
