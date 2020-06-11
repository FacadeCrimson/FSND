
### Configure Enviornment Variables

Ionic uses a configuration file to manage environment variables. These variables ship with the transpiled software and should not include secrets.

- Open `./src/environments/environments.ts` and ensure each variable reflects the system you stood up for the backend.

## Running Your Frontend in Dev Mode

Ionic ships with a useful development server which detects changes and transpiles as you work. The application is then accessible through the browser on a localhost port. To run the development server, cd into the `frontend` directory and run:

```bash
ionic serve
```

>_tip_: Do not use **ionic serve**  in production. Instead, build Ionic into a build artifact for your desired platforms.
[Checkout the Ionic docs to learn more](https://ionicframework.com/docs/cli/commands/build)

### Authentication

The authentication system used for this project is Auth0. `./src/services/auth.service.ts` contains the logic to direct a user to the Auth0 login page, managing the JWT token upon successful callback, and handle setting and retrieving the token from the local store. This token is then consumed by our DrinkService (`./src/services/auth.service.ts`) and passed as an Authorization header when making requests to our backend.

### Authorization

The Auth0 JWT includes claims for permissions based on the user's role within the Auth0 system. This project makes use of these claims using the `auth.can(permission)` method which checks if particular permissions exist within the JWT permissions claim of the currently logged in user. This method is defined in  `./src/services/auth.service.ts` and is then used to enable and disable buttons in `./src/pages/drink-menu/drink-form/drink-form.html`.


## Tasks
7. Test your endpoints with [Postman](https://getpostman.com). 
    - Right-clicking the collection folder for barista and manager, navigate to the authorization tab, 
    - Run the collection and correct any errors.
    - Export the collection overwriting the one we've included so that we have your proper JWTs during review!

### Implement The Server

There are `@TODO` comments throughout the `./backend/src`. We recommend tackling the files in order and from top to bottom:

1. `./src/auth/auth.py`
2. `./src/api.py`

Auth url:
https://simontan.auth0.com/authorize?audience=second&response_type=token&client_id=ysceJJiwTpES1QH6Kya4NPLNV4dQRgJv&redirect_uri=https://127.0.0.1/login_results

Barista
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InVZMlpDdUlNb3Z4MEE5RkVuTmFuRSJ9.eyJpc3MiOiJodHRwczovL3NpbW9udGFuLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWUyNGU2ZTdlMDMzNzAwMTRhNDE2NGUiLCJhdWQiOiJzZWNvbmQiLCJpYXQiOjE1OTE4ODk5MjcsImV4cCI6MTU5MTg5NzEyNywiYXpwIjoieXNjZUpKaXdUcEVTMVFINkt5YTROUExOVjRkUVJnSnYiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImdldDpkcmlua3MtZGV0YWlsIl19.2pZgkrGsfUg00qvbxUMEInJ8lk8qk4qDGMsUtoydMHiKlsqBhEtCeyVBNVjF2rb0CHm4CR_HMFuhQukdcP2BFTp7B7hNEmmOoAE3I0cUejS3ynl1iSFZzgIZGVnIMMtklb0KWoj7dH-tpRn5b7oK8qoJIgPIU0eeGlp6iMAQFdzYfrWAZclDvnVwpTaWD9IbJ3lRf-PYgC4pOIFOlNUy2JSzEIZHDTJBv24axcwXTaZG7A4rs9EfJA6TSE-8pIe7l7XDkQ4joSloX4MGWbzBmpb5GG9ATlU6cXZj1BinOQ_1-o8E2iEAIrGMyQe94RVU1FUv60oTPkbmmgdn4VnKZA

Manager
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6InVZMlpDdUlNb3Z4MEE5RkVuTmFuRSJ9.eyJpc3MiOiJodHRwczovL3NpbW9udGFuLmF1dGgwLmNvbS8iLCJzdWIiOiJhdXRoMHw1ZWUyNGVjYzFiMjQwYTAwMTMyM2FkZmQiLCJhdWQiOiJzZWNvbmQiLCJpYXQiOjE1OTE4OTAwNTMsImV4cCI6MTU5MTg5NzI1MywiYXpwIjoieXNjZUpKaXdUcEVTMVFINkt5YTROUExOVjRkUVJnSnYiLCJzY29wZSI6IiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTpkcmlua3MiLCJnZXQ6ZHJpbmtzLWRldGFpbCIsInBhdGNoOmRyaW5rcyIsInBvc3Q6ZHJpbmtzIl19.lPIadgeOCsbiU7J36GfklS5xGoq8J1bm7Rt2HVWw5Dixk4wHKdlw08lxruD1R80uvFSxnGAEuNHCmqnFgk3ytHpE-CWHcpcX-pHO8eqzh3CkQ-x9LU0Y_KGC6ThR2ZQHPqGliK9-bwrZCZ13Gchi_EXsn7W0f-rz_YfRVMo34zheeap5u6ATv8Vw7ujXMTQoMEMIW1DTZYI934h7kWYTCEbWSBMYCuo7ugKOJe7IZshtL6HfkCXksrKEa3cKUqJX_jkVgofPdmQuP2pWuhiagxk26bzfTPdy55unNTguPttS_lKMpyQ3x_mDw-h2ftBXcVyQjnPg7NlgSiPIejKlOQ