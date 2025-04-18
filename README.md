# Objective

To create a web app that takes a CSV file and a HTML Template from the user. The template will contain special variables like {name} ,{age} etc. which will be replaced by the value given in the CSV File.

## Example

**HTML Template:-**

```
Hello {name}! Your password is {password} and username is {username}
```

**CSV File:-**

| Email            | Name    | Password       | Username     |
| ---------------- | ------- | -------------- | ------------ |
| <user@gmail.com> | User123 | strongpassword | username1234 |

The preview of the HTML template will be

```
Hello User123! Your password is strongpassword and username is username1234
```

# Frontend

- A home page with the name of the project with contributors at the bottom.
- "Login/Signup with google" page.
- Main page where user uploads HTML template and CSV file. (If HTML template contains {} type variables, ask user from which field to take the values from).

# Backend endpoint

- OAuth2
- Uploading CSV file and template
- Replacing {} variables with the one in CSV file
- Send email to recipient using multiple workers(asynchronous).

