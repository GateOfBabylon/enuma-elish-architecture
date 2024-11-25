## HTTP Executions

### Пример 1: Създаване и актуализиране на ресурс, ако не съществува

Този екзекутор проверява дали даден ресурс съществува. Ако не съществува, създава го и след това го актуализира.

```ea
executor:
  name: "create-or-update-resource"
  type: "http"
  env:
    user: "my_username"
    pass: ${{password}}
    id: "12345"
  tasks:
    - name: "ensure-token"
      method: "POST"
      url: "http://example.com/api/token"
      headers:
        Content-Type: "application/json"
      body: '{"username":${{user}}, "password":${{pass}}}'
      export: ${{token}}

    - name: "check-existing"
      method: "GET"
      url: "http://example.com/api/resource/${{id}}"
      headers:
        Authorization: "Bearer ${{token}}"
      export: ${{exists}}

    - name: "create-resource"
      method: "POST"
      condition: !${{exists}}
      url: "http://example.com/api/resource"
      headers:
        Authorization: "Bearer ${{token}}"
        Content-Type: "application/json"
      body: '{"id":${{id}}, "data":"new data"}'

    - name: "update-resource"
      method: "PUT"
      condition: ${{exists}}
      url: "http://example.com/api/resource/${{id}}"
      headers:
        Authorization: "Bearer ${{token}}"
        Content-Type: "application/json"
      body: '{"data":"updated data"}'
```

### Пример 2: Регистрация на потребител и изпращане на потвърждение по имейл

Този екзекутор проверява дали потребител със специфичен имейл съществува, ако не, създава нов потребител и изпраща потвърдителен имейл.

```ea
executor:
  name: "register-and-confirm-user"
  type: "http"
  env:
    admin_user: "admin"
    admin_pass: ${{admincreds.password}}
    email: "user@example.com"
  tasks:
    - name: "admin-login"
      method: "POST"
      url: "http://example.com/api/admin/login"
      headers:
        Content-Type: "application/json"
      body: '{"username":${{admin_user}}, "password":${{admin_pass}}}'
      export: ${{admin_token}}

    - name: "check-user-exists"
      method: "GET"
      url: "http://example.com/api/users?email=${{email}}"
      headers:
        Authorization: "Bearer ${{admin_token}}"
      export: ${{user_exists}}

    - name: "create-user"
      method: "POST"
      condition: !${{user_exists}}
      url: "http://example.com/api/users"
      headers:
        Authorization: "Bearer ${{admin_token}}"
        Content-Type: "application/json"
      body: '{"email":${{email}}, "role":"user"}'
      export: ${{user_id}}

    - name: "send-confirmation"
      method: "POST"
      condition: ${{user_exists && user_id}}
      url: "http://example.com/api/users/${{user_id}}/send-confirmation"
      headers:
        Authorization: "Bearer ${{admin_token}}"
        Content-Type: "application/json"
      body: '{"email":${{email}}}'
```

### Пример 3: Събиране на данни и изпращане на съобщение в случай на грешка

Този екзекутор извършва няколко последователни GET заявки за събиране на данни от различни ресурси. Ако нещо липсва, изпраща нотификация за грешка.

```ea
executor:
  name: "collect-data-and-notify"
  type: "http"
  env:
    api_key: "super_secret_key"
    alert_email: "alerts@example.com"
  tasks:
    - name: "fetch-user-data"
      method: "GET"
      url: "http://example.com/api/users/data"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: ${{user_data}}
      delay: 2000

    - name: "fetch-order-history"
      method: "GET"
      url: "http://example.com/api/orders/history"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: ${{order_history}}
      timeout: 5000

    - name: "fetch-payment-info"
      method: "GET"
      url: "http://example.com/api/payments/info"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: ${{payment_info}}
      delay: 2000

    - name: "send-success-notification"
      condition: ${{user_data && order_history && payment_info}}
      method: "POST"
      url: "http://example.com/api/alerts/success"
      headers:
        Content-Type: "application/json"
      body: '{"email":${{alert_email}}, "message":"Data collection complete"}'

    - name: "send-error-notification"
      condition: !${{user_data && order_history && payment_info}}
      method: "POST"
      url: "http://example.com/api/alerts"
      headers:
        Content-Type: "application/json"
      body: '{"email":${{alert_email}}, "message":"Data collection incomplete"}'
```

### Пример 4: Масово изтриване на ресурси с iterate

Този екзекутор изпълнява последователност от изтриване на множество ресурси, ако са намерени, като ползва предишен резултат за избор на ресурси.

```ea
executor:
  name: "bulk-delete-resources"
  type: "http"
  env:
    api_key: "another_secret_key"
  tasks:
    - name: "list-resources"
      method: "GET"
      url: "http://example.com/api/resources"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: "${{resource_list}}"
    - name: "delete-resources"
      iterate: "${{resource_list}}"
      method: "DELETE"
      url: "http://example.com/api/resources/${{item}}"
      headers:
        Authorization: "Bearer ${{api_key}}"
```

### Пример 5: Потвърждение на статус на ресурс

Този екзекутор проверява статуса на ресурс, чака малко, ако ресурсът не е готов, и го потвърждава само при успех.

```ea
executor:
  name: "confirm-resource-status"
  type: "http"
  env:
    api_key: "my_api_key"
    resource_id: "resource_123"
  tasks:
    - name: "check-status"
      method: "GET"
      url: "http://example.com/api/resources/${{resource_id}}/status"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: "${{status}}"

    - name: "wait-for-ready"
      condition: "${{status != 'ready'}}"
      timeout: 5000
      retry: 3

    - name: "process-status"
      try:
        - if: "${{status == 'ready'}}"
          method: "POST"
          url: "http://example.com/api/resources/${{resource_id}}/confirm"
          headers:
            Authorization: "Bearer ${{api_key}}"
        - if: "${{status == 'pending'}}"
          method: "POST"
          url: "http://example.com/api/resources/${{resource_id}}/queue-for-review"
          headers:
            Authorization: "Bearer ${{api_key}}"
        - if: "${{status == 'error'}}"
          method: "POST"
          url: "http://example.com/api/resources/${{resource_id}}/report-error"
          headers:
            Authorization: "Bearer ${{api_key}}"
      else:
        method: "POST"
        url: "http://example.com/api/resources/${{resource_id}}/reject"
        headers:
            Authorization: "Bearer ${{api_key}}"
```

### Пример 6: Извличане на списък, паралелно събиране на данни и обработка на всеки елемент

Извлича списък от елементи, съхранява ги в items, след което паралелно изпраща заявки за детайли и статистика за всеки елемент, и накрая изпраща POST заявка за обработка на всеки елемент.

``` ea
executor:
  name: "fetch-and-process-items"
  type: "http"
  env:
    api_key: "secure_api_key"
  tasks:
    - name: "fetch-item-list"
      method: "GET"
      url: "http://example.com/api/items"
      headers:
        Authorization: "Bearer ${{api_key}}"
      export: "${{items}}"

    - name: "fetch-additional-data-parallel"
      parallel:
        - name: "fetch-item-details"
          iterate: "${{items}}"
          method: "GET"
          url: "http://example.com/api/items/${{item.id}}/details"
          headers:
            Authorization: "Bearer ${{api_key}}"
          export: "${{item.details}}"

        - name: "fetch-item-stats"
          iterate: "${{items}}"
          method: "GET"
          url: "http://example.com/api/items/${{item.id}}/stats"
          headers:
            Authorization: "Bearer ${{api_key}}"
          export: "${{item.stats}}"

    - name: "process-each-item"
      iterate: "${{items}}"
      method: "POST"
      url: "http://example.com/api/process/${{item.id}}"
      headers:
        Authorization: "Bearer ${{api_key}}"
        Content-Type: "application/json"
      body: '{"details":${{item.details}}, "stats":${{item.stats}}}'
```

## Python Executions

### Пример 1: Проверка за съществуване на файл и създаване, ако липсва

Този екзекутор изпълнява Python скрипт, който проверява дали даден файл съществува. Ако не съществува, го създава и добавя начално съдържание.

```ea
executor:
  name: "check-or-create-file"
  type: "py"
  universe:
    world: "docker.io/python-file-handler:latest"
    secret: "file_handler_registry_credentials"
  env:
    file_path: "/data/config.json"
    content: '{"default": "config"}'
  tasks:
    - name: "check-file-exists"
      script: |
        import os
        exists = os.path.isfile("${{file_path}}")
        print("File exists:", exists)
      export: "${{file_exists}}"

    - name: "create-file"
      try:
        - if: "!${{file_exists}}"
        script: |
            with open("${{file_path}}", "w") as f:
                f.write("${{content}}")
            print("File created with default content.")
```

### Пример 2: Изпълнение на основен Python скрипт с параметри

Този екзекутор зарежда и изпълнява основен Python скрипт с подадени параметри от околната среда. Ако скриптът успее, записва резултата в променлива.

```ea
executor:
  name: "run-main-script"
  type: "py"
  universe:
    world: "docker.io/main-script-runner:latest"
    secret: "main_script_registry_credentials"
  env:
    arg1: "data_set_1"
    arg2: "run_analysis"
  tasks:
    - name: "execute-main-script"
      scriptPath: "./scripts/main_script.py ${{arg1}} ${{arg2}}"
      export: "${{output}}"

    - name: "log-result"
      script: |
        print("Script output:", "${{output}}")
```

### Пример 3: Събиране на данни и изпращане на съобщение в случай на грешка

Този екзекутор изпълнява няколко Python скрипта, които събират данни от различни източници. Ако някое събиране не е успешно, изпраща съобщение за грешка.

```ea
executor:
  name: "collect-data-and-notify"
  type: "py"
  universe:
    world: "docker.io/data-collector:latest"
    secret: "data_collector_registry_credentials"
  env:
    alert_email: "alerts@example.com"
  tasks:
    - name: "fetch-user-data"
      script: |
        user_data = {"name": "John", "id": 123}
        print("User data fetched.")
      export: "${{user_data}}"

    - name: "fetch-order-history"
      script: |
        order_history = ["order1", "order2"]
        print("Order history fetched.")
      export: "${{order_history}}"

    - name: "fetch-payment-info"
      script: |
        payment_info = {"last_payment": "2023-10-05"}
        print("Payment info fetched.")
      export: "${{payment_info}}"

    - name: "send-notification"
      try:
        - if: "${{user_data && order_history && payment_info}}"
          script: |
            print("Data collection complete. Sending success notification to:", "${{alert_email}}")
        - if: "!${{user_data && order_history && payment_info}}"
          script: |
            print("Data collection incomplete. Sending error notification to:", "${{alert_email}}")
```

### Пример 4: Паралелно изпълнение на скриптове и обработка на всеки елемент в списък

Този екзекутор първо извлича списък от елементи, след това паралелно изпълнява два Python скрипта за събиране на различни данни за всеки елемент и накрая изпраща резултатите за обработка.

```ea
executor:
  name: "fetch-and-process-items"
  type: "py"
  universe:
    world: "docker.io/item-processor:latest"
    secret: "item_processor_registry_credentials"
  env:
    items: [{"id": 1}, {"id": 2}, {"id": 3}]
  tasks:
    - name: "fetch-item-list"
      scriptPath: "./scripts/load_items.py"
      export: "${{items}}"

    - name: "fetch-additional-data-parallel"
      parallel:
        - name: "fetch-item-details"
          iterate: "${{items}}"
          scriptPath: "./scripts/fetch_item_details.py ${{item.id}}"
          export: "${{item.details}}"

        - name: "fetch-item-stats"
          iterate: "${{items}}"
          scriptPath: "./scripts/fetch_item_stats.py ${{item.id}}"
          export: "${{item.stats}}"

    - name: "process-each-item"
      iterate: "${{items}}"
      scriptPath: "./scripts/process_item.py ${{item.id}} ${{item.details}} ${{item.stats}}"
```

### Пример 5: Проверка за статус и изпълнение на Python скрипт при различни условия

Този екзекутор първо проверява статус и изпълнява съответния скрипт въз основа на резултата.

```ea
executor:
  name: "confirm-or-reject-status"
  type: "py"
  universe:
    world: "docker.io/my-docker-image:latest"
    secret: "my_docker_registry_credentials"
  env:
    status: "pending"
  tasks:
    - name: "check-status"
      scriptPath: "./scripts/check_status.py"
      export: ${{status}}

    - name: "wait-for-ready"
      scriptPath: "./scripts/wait_for_ready.py ${{status}}"

    - name: "confirm-or-reject"
      try:
        - if: ${{status == 'ready'}}
          task:
            scriptPath: "./scripts/confirm_resource.py"
        - if: ${{status == 'pending'}}
          task:
            scriptPath: "./scripts/queue_resource_for_review.py"
        - if: ${{status == 'error'}}
          task:
            scriptPath: "./scripts/report_resource_error.py"
      else:
        scriptPath: "./scripts/reject_resource.py"
```