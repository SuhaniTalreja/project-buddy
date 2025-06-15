Okay, since you haven't specified a technology stack, I'll provide examples using plain HTML, CSS, and JavaScript for a simple in-page button and then a redirect example.  Remember to adapt this to your specific project structure.

**Example 1: In-page login button (simple example -  no actual login functionality)**

```html
<!DOCTYPE html>
<html>
<head>
<title>Homepage</title>
<style>
  #navbar {
    background-color: #f0f0f0;
    padding: 10px;
  }
  #loginButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    cursor: pointer;
  }
</style>
</head>
<body>

<div id="navbar">
  <button id="loginButton">Login</button>
</div>

<script>
  const loginButton = document.getElementById('loginButton');
  loginButton.addEventListener('click', () => {
    alert('Login button clicked!  (This is a placeholder.  Add actual login logic here.)');
    //  In a real application, you'd replace this with AJAX to a backend and UI updates.
  });
</script>

</body>
</html>
```

**Example 2: Redirect to login page**

```html
<!DOCTYPE html>
<html>
<head>
<title>Homepage</title>
<style>
  #navbar {
    background-color: #f0f0f0;
    padding: 10px;
  }
  #loginButton {
    background-color: #4CAF50;
    border: none;
    color: white;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    cursor: pointer;
    text-decoration: none; /* Remove underline from link */
  }
</style>
</head>
<body>

<div id="navbar">
  <a href="/login" id="loginButton">Login</a>  <!-- Replace /login with your actual login URL -->
</div>

</body>
</html>
```

Remember to replace `/login` with the correct path to your login page in Example 2.  These are very basic examples.  A real-world application would likely involve more sophisticated styling, error handling, and server-side interaction for user authentication.  Provide your tech stack details for a more tailored response.