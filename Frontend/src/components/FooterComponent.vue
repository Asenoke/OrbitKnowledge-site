<script setup>

</script>

<template>
  <!-- Подвал -->
  <footer class="footer">
    <div class="container">
      <div class="footer__content">
        <div class="footer-col">
          <a href="#" class="logo footer-logo">
            <i class="fas fa-rocket"></i>
            <span>Орбита<span class="logo-accent">Знаний</span></span>
          </a>
          <p>Образовательный некоммерческий проект для детей и подростков. Изучаем историю, чтобы строить будущее.</p>
          <div class="social-links">
            <a href="#"><i class="fab fa-vk"></i></a>
            <a href="#"><i class="fab fa-telegram"></i></a>
            <a href="#"><i class="fab fa-youtube"></i></a>
          </div>
        </div>
        <div class="footer-col">
          <h4>Разделы</h4>
          <ul>
            <li><a href="#heroes">Герои</a></li>
            <li><a href="#missions">Миссии</a></li>
            <li><a href="#timeline">Лента времени</a></li>
            <li><a href="#future">КБ Будущего</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Для родителей и учителей</h4>
          <ul>
            <li><a href="#">Методические материалы</a></li>
            <li><a href="#">Безопасность</a></li>
            <li><a href="#">Вопросы и ответы</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>Оставайтесь на связи</h4>
          <p>Подпишитесь на новости о новых миссиях и событиях.</p>
          <form class="subscribe-form">
            <input type="email" placeholder="Ваш e-mail" required>
            <button type="submit" id="submit"><i class="fas fa-paper-plane"></i></button>
          </form>
        </div>
      </div>
      <div class="footer-bottom">
        <p>&copy; 2026 Орбита Знаний. Проект для образовательных целей. Все имена и события принадлежат истории.</p>
        <p>Иконки от <a href="https://icons8.com" target="_blank">Icons8</a>, изображения от <a href="https://unsplash.com" target="_blank">Unsplash</a>.</p>
      </div>
    </div>
  </footer>

</template>

<style scoped>
/* Подвал */
.footer {
  background-color: var(--dark-color);
  color: white;
  padding: 70px 0 30px;
}

.footer__content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 50px;
}

.footer-col h4 {
  margin-bottom: 20px;
  color: white;
}

.footer-col ul {
  list-style: none;
}

.footer-col ul li {
  margin-bottom: 10px;
}

.footer-col ul li a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: var(--transition);
}

.footer-col ul li a:hover {
  color: var(--secondary-color);
  padding-left: 5px;
}

.social-links {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.social-links a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  transition: var(--transition);
}

.social-links a:hover {
  background-color: var(--secondary-color);
  transform: translateY(-5px);
}

.subscribe-form {
  display: flex;
  margin-top: 15px;
}

.subscribe-form input {
  flex-grow: 1;
  padding: 12px 15px;
  border: none;
  border-radius: 50px 0 0 50px;
  font-family: var(--font-body);
}

.subscribe-form button {
  background-color: var(--secondary-color);
  color: white;
  border: none;
  border-radius: 0 50px 50px 0;
  padding: 0 20px;
  cursor: pointer;
  transition: var(--transition);
}

.subscribe-form button:hover {
  background-color: var(--primary-color);
}

.footer-bottom {
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

.footer-bottom a {
  color: var(--secondary-color);
  text-decoration: none;
}

</style>