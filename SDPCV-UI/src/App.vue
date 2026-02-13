<template>
  <div class="app">

    <!-- HEADER -->
    <header>
      <h1>SDPCV</h1>
      <nav>
        <router-link to="/">Video</router-link>
        <router-link to="/analytics">Analytics</router-link>
      </nav>
    </header>

    <!-- CONTENT -->
    <div class="content">
      <router-view />
    </div>

  </div>
</template>

<style>
.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', sans-serif;
}

header {
  height: 60px;
  background: #1e1e2f;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 25px;
}

nav a {
  color: white;
  margin-left: 25px;
  text-decoration: none;
  font-weight: 500;
}

nav a.router-link-active {
  border-bottom: 2px solid #00ff88;
}

.content {
  flex: 1;
  background: #111;
}
</style>