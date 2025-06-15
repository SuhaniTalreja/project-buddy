Because the prompt doesn't specify a framework, I'll provide examples using plain HTML, CSS, and optional JavaScript, and then show a React example.

**1. Plain HTML, CSS, and JavaScript:**

```html
<!DOCTYPE html>
<html>
<head>
<title>Navbar with Login Button</title>
<style>
nav {
  background-color: #f0f0f0;
  padding: 10px;
  display: flex; /* Use flexbox for easy alignment */
  justify-content: space-between; /* Distribute space between left and right */
}

.navbar-right {
  /* No extra styling needed with flexbox */
}

#login-button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 5px;
  cursor: pointer;
}
</style>
</head>
<body>

<nav>
  <div class="navbar-left">
    <a href="#">Home</a>
    <a href="#">About</a>
  </div>
  <div class="navbar-right">
    <button id="login-button">Login</button>
  </div>
</nav>

<script>
  const loginButton = document.getElementById('login-button');
  loginButton.addEventListener('click', () => {
    // Add your login logic here.  For example, redirect to a login page:
    window.location.href = '/login';
  });
</script>

</body>
</html>
```

**2. React Example:**

```jsx
import React from 'react';

const Navbar = () => {
  const handleLoginClick = () => {
    // Add your login logic here, e.g., using a routing library like react-router-dom
    console.log('Login button clicked!');
  };

  return (
    <nav>
      <div className="navbar-left">
        <a href="#">Home</a>
        <a href="#">About</a>
      </div>
      <div className="navbar-right">
        <button onClick={handleLoginClick}>Login</button>
      </div>
    </nav>
  );
};

export default Navbar;


// CSS (can be in a separate .css file or styled-components)
/*  This CSS would likely be in a separate file or within a styled-component  */
/*nav {
  background-color: #f0f0f0;
  padding: 10px;
  display: flex;
  justify-content: space-between;
}

.navbar-right {
}

button {
  background-color: #4CAF50;
  border: none;
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 5px;
  cursor: pointer;
}*/
```

Remember to adapt the JavaScript portion to your specific authentication method (e.g., using a library like Firebase or Auth0).  The React example is a basic component; you would integrate it into your larger application's component structure.  You'll also need to include CSS, either via a separate stylesheet linked to the HTML file or using styled-components or similar within your React code.  Remember to install `react-router-dom` if you want to use the routing capabilities.