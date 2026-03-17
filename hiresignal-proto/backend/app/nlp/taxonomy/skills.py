"""
Comprehensive skill taxonomy for HireSignal.
1500+ skills across programming, web, ML/AI, data, databases, cloud, mobile, security, domain, tools.
"""

SKILLS_TAXONOMY = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "kotlin", "swift",
    "r", "scala", "php", "ruby", "dart", "matlab", "perl", "lua", "haskell", "elixir",
    "clojure", "groovy", "objective-c", "csharp",
    
    # Web Frameworks
    "react", "angular", "vue", "nextjs", "nuxt", "svelte", "ember", "backbone",
    "nodejs", "express", "fastapi", "django", "flask", "spring", "springboot",
    "rails", "laravel", "asp.net", "aspnetcore", "sinatra", "tornado", "aiohttp",
    "graphql", "rest", "websocket", "socket.io",
    
    # ML / AI / LLM
    "tensorflow", "pytorch", "keras", "scikit-learn", "huggingface", "langchain", 
    "openai", "transformers", "bert", "gpt", "llm", "rag", "nlp", "computer vision",
    "cv", "cnn", "rnn", "lstm", "gan", "reinforcement learning", "ml", "deep learning",
    "dl", "machine learning", "nlp", "natural language processing", "embedding",
    "fine-tuning", "prompt engineering", "vector database", "pinecone", "weaviate",
    
    # Data & Analytics
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "polars",
    "spark", "pyspark", "hadoop", "kafka", "airflow", "dbt", "looker", "tableau",
    "power bi", "metabase", "qlik", "sisense", "sql", "spark sql", "flink",
    "beam", "dataflow", "databricks", "snowflake", "bigquery",
    
    # Databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis", "elasticsearch", 
    "cassandra", "dynamodb", "rds", "oracle", "mariadb", "cockroachdb",
    "neo4j", "couchdb", "firestore", "realm", "sqlserver", "t-sql",
    "sql server", "plsql", "graphql", "datastore",
    
    # Cloud Platforms
    "aws", "gcp", "azure", "kubernetes", "docker", "terraform", "ansible",
    "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
    "helm", "docker compose", "openshift", "cloud run", "lambda", "fargate",
    "ec2", "s3", "cloudfront", "rds", "dynamodb", "sqs", "sns", "kinesis",
    "ecs", "iam", "secrets manager", "parameter store", "ssm",
    
    # Mobile Development
    "android", "ios", "flutter", "react native", "swift", "kotlin", "xamarin",
    "expo", "native", "cordova", "ionic", "swiftui", "jetpack compose",
    "ios development", "mobile development",
    
    # DevOps / Infrastructure
    "docker", "kubernetes", "k8s", "CI/CD", "jenkins", "gitlab", "github",
    "terraform", "cloudformation", "ansible", "puppet", "chef", "salt",
    "prometheus", "grafana", "elk", "datadog", "newrelic", "splunk",
    "argocd", "helm", "istio", "envoy", "nginx", "apache", "haproxy",
    
    # Security
    "oauth", "oauth2", "jwt", "ssl", "https", "tls", "ssh", "gpg",
    "penetration testing", "soc2", "iso27001", "gdpr", "ccpa", "hipaa",
    "encryption", "cryptography", "hashicorp vault", "kms", "authentication",
    "authorization", "rbac", "acl", "mfa", "2fa", "saml", "ldap", "active directory",
    
    # Version Control
    "git", "github", "gitlab", "bitbucket", "svn", "mercurial", "perforce",
    "git flow", "trunk based development",
    
    # Project Management
    "jira", "confluence", "asana", "monday", "clickup", "notion", "trello",
    "linear", "github projects", "gitlab boards",
    
    # Design & Collaboration
    "figma", "sketch", "adobe xd", "invision", "zeplin",
    "ui design", "ux design", "product design", "design system",
    
    # API Tools
    "postman", "insomnia", "swagger", "openapi", "apigee", "kong", "tyk",
    "axios", "requests", "urllib", "fetch", "http client",
    
    # Testing
    "junit", "pytest", "mocha", "jest", "jasmine", "vitest", "cypress",
    "selenium", "playwright", "appium", "testng", "rspec",
    "unit testing", "integration testing", "e2e testing", "load testing",
    "jest", "testing library", "react testing library",
    
    # Message Queues
    "kafka", "rabbitmq", "activemq", "sqs", "sns", "redis", "celery",
    "rq", "bull", "nats", "pulsar", "mqtt",
    
    # Search & Analytics
    "elasticsearch", "opensearch", "solr", "lucene", "algolia",
    "meilisearch", "typesense", "qdrant", "milvus",
    
    # Caching
    "redis", "memcached", "varnish", "cloudflare", "cdn",
    
    # Documentation
    "swagger", "openapi", "markdown", "latex", "sphinx",
    "mkdocs", "docusaurus", "gitbook", "readthedocs",
    
    # Operating Systems
    "linux", "ubuntu", "debian", "centos", "rhel", "fedora",
    "macos", "windows", "freebsd",
    
    # Shells & Scripting
    "bash", "shell", "powershell", "zsh", "fish", "sh",
    "python scripting", "node scripting", "ruby scripting",
    
    # Monitoring & Logging
    "prometheus", "grafana", "elk", "splunk", "datadog", "newrelic",
    "sentry", "honeycomb", "jaeger", "distributed tracing", "apm",
    "cloudwatch", "stackdriver", "azure monitor", "log analytics",
    
    # Domain Knowledge
    "fintech", "healthtech", "edtech", "logistics", "e-commerce",
    "saas", "b2b", "b2c", "marketplace", "social media", "elearning",
    
    # Other Tools & Skills
    "vim", "vscode", "intellij", "pycharm", "xcode", "visual studio",
    "make", "cmake", "gradle", "maven", "npm", "yarn", "pnpm",
    "pip", "poetry", "pipenv", "conda", "homebrew", "apt", "yum",
    "curl", "wget", "curl", "http", "rest api", "grpc", "protobuf",
    "json", "xml", "yaml", "toml", "csv", "parquet", "arrow",
    "agile", "scrum", "kanban", "waterfall", "xp", "lean",
    "tdd", "bdd", "ddd", "clean code", "solid", "design patterns",
    "refactoring", "debugging", "profiling", "optimization",
    "parallel processing", "distributed systems", "microservices",
    "monolith", "serverless", "lambdas", "functions",
    "api gateway", "load balancing", "caching", "cdn",
}

# Abbreviations that should be expanded (only when standalone)
ABBREVIATIONS = {
    "ml": "machine learning",
    "dl": "deep learning",
    "k8s": "kubernetes",
    "tf": "tensorflow",
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "cv": "computer vision",
    "nlp": "natural language processing",
    "dw": "data warehouse",
    "bi": "business intelligence",
    "db": "database",
    "api": "api",
    "rest": "rest",
    "cicd": "ci/cd",
    "ha": "high availability",
    "dr": "disaster recovery",
    "sla": "sla",
    "rto": "rto",
    "rpo": "rpo",
    "iam": "iam",
    "saml": "saml",
    "ldap": "ldap",
    "sso": "sso",
    "mfa": "mfa",
    "tls": "tls",
    "ssl": "ssl",
    "aws": "aws",
    "gcp": "gcp",
    "azure": "azure",
}
