<section>
  <div class="center">
    <h1 class="success">Flower Seal Management</h1>
    <p>This application is flowersale where you can see and buy different categories of flowers. Authentication system is also added in this 
     application. I used Django Rest Framework to build this application.</p>
    <ol>
      <li>Admin</li>
      <li>User</li>
    </ol>
    <h2>Functional Requirements</h2>
    <h3>Users</h3>
    <ul>
      <li>User can register.</li>
      <li>User can login, logout</li>
    </ul>
    <h3>Flowers</h3>
    <ul>
      <li>You can see the list of all the flowers and the details of the flowers.</li>
      <li>You can see the reviews that users have given in flowers.</li>
      <li>Here are some tips for caring for flowers.</li>
    </ul>
     <h3>Orders</h3>
    <ul>
      <li>You can order</li>
      <li>You will see the orders you have placed</li>
      <li>You can view order summaries.</li>
    </ul>
    <h3>Profiles</h3>
    <ul>
      <li>User can see his profile.</li>
      <li>User can also change password.</li>
    </ul>
    <h3>Admins</h3>
    <ul>
      <li>Lists of users can be seen.</li>
      <li>Lists of users can be seen in details.</li>
      <li>User admin can be seen.</li>
      <li>You will see the list of posts</li>
      <li>You will see the details of the post.</li>
      <li>The status of the order can be seen.</li>
    </ul>
    <h3>Payment</h3>
    <ul>
      <li>SSL Commerce added for payment.</li>
    </ul>
    <h1>API Endpoints</h1>
    <h3>Users</h3>
    <ul>
      <li>POST/users/register/</li>
      <li>POST/users/login/</li>
      <li>GET/users/logout/</li>
      <li>GET,POST/users/users/</li>
    </ul>
    <h3>Flowers</h3>
    <ul>
      <li>GET, POST/flowers/flowers/</li>
      <li>GET, POST//flowers/comments/</li>
      <li>GET, POST//flowers/comments/</li>
      <li>GET,POST/flowers/care-tips/</li>
    </ul>
    <h3>Order</h3>
    <ul>
      <li>POST/orders/create_order/</li>
      <li>GET, POST/orders/my_orders/</li>
      <li>GET/orders/order_summary/</li>
    </ul>
    <h3>Proiles</h3>
    <ul>
      <li>GET, PUT/profiles/user/2/</li>
      <li>POST/profiles/pass_cng/</li>
    </ul>
    <h3>Admins</h3>
    <ul>
      <li>GET, POST/admins/post_list/</li>
      <li>GET, PUT, DELETE/admins/post_detail/1/</li>
      <li>GET/admins/is_admin/</li>
      <li>GET/admins/user_list/</li>
      <li>GET, PUT/admins/user_detail/1/</li>
      <li>GET/admins/order-stats/</li>
    </ul>
    <h3>Payment</h3>
    <ul>
      <li>GET or POST/payment/payment</li>
    </ul>
    <h4>Postman Documenttaion : <a href="https://www.postman.com/downloads/?utm_source=postman-home">Download 64-bit</a></h4>
  </div>
</section>
