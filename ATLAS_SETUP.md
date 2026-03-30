# MongoDB Atlas Setup Guide

RAKSHAK uses MongoDB Atlas as its database since it requires geospatial (2dsphere) indexing and is lightweight for storing dynamic documents. Best of all, they offer a **free** cluster that will not expire.

## Step 1: Sign Up
1. Go to [MongoDB Atlas Registration](https://www.mongodb.com/cloud/atlas/register).
2. Create an account. No credit card is required.

## Step 2: Create a Cluster
1. Once logged in, click **"Build a Database"**.
2. Select the **FREE M0 tier**.
3. Choose the nearest region to you.
4. Click **Create Cluster**.

## Step 3: Setup Database User
1. Go to **Database Access** under the Security menu on the left sidebar.
2. Click **Add New Database User**.
3. Choose Password authentication.
4. **Username**: \`rakshak_user\`
5. **Password**: (Auto-generate a strong password and save it)
6. **Role**: \`readWriteAnyDatabase\` (or specifically on \`rakshak_db\`).
7. Click **Add User**.

## Step 4: Network Access
1. Go to **Network Access** under the Security menu on the left sidebar.
2. Click **Add IP Address**.
3. Click **"Allow Access from Anywhere"** (\`0.0.0.0/0\`). *Note: This is just to make local testing easier. Once you deploy, restrict this to your server's IP address.*
4. Click **Confirm**.

## Step 5: Get Connection String
1. Go to **Database** under the Deployment menu on the left sidebar.
2. Click the **Connect** button on your cluster.
3. Select **Drivers**.
4. Set Node to **Python**.
5. Copy the connection string.

It will look something like this:
\`mongodb+srv://rakshak_user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority\`

## Step 6: Configure your \`.env\` file
Replace \`<password>\` with the password you generated, and append \`rakshak_db\` right before the query parameters:

\`mongodb+srv://rakshak_user:yourpassword123@cluster0.xxxxx.mongodb.net/rakshak_db?retryWrites=true&w=majority\`

Save this as your \`MONGODB_URI\` in the \`.env\` file.
