// Learn more about clients at https://docs.boundaryml.com/docs/snippets/clients/overview

client<llm> DietModel {
  provider openai
  retry_policy Exponential
  options {
    model "gpt-4o-mini"
    api_key env.MY_OPENAI_KEY
    max_tokens 4096
    temperature 0.7
    http {
      connect_timeout_ms 5000
      request_timeout_ms 120000  // 2 minutes timeout for diet generation
    }
  }
}

client<llm> ReceipeModel {
  provider openai
  retry_policy Constant
  options {
    model "gpt-4o-mini"
    api_key env.MY_OPENAI_KEY
    max_tokens 2048
    temperature 0.7
    http {
      connect_timeout_ms 3000
      request_timeout_ms 60000  // 1 minute timeout for recipe generation
    }
  }
}

// https://docs.boundaryml.com/docs/snippets/clients/retry
retry_policy Constant {
  max_retries 3
  // Strategy is optional
  strategy {
    type constant_delay
    delay_ms 200
  }
}

retry_policy Exponential {
  max_retries 2
  // Strategy is optional
  strategy {
    type exponential_backoff
    delay_ms 300
    multiplier 1.5
    max_delay_ms 10000
  }
}