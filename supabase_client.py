from supabase import create_client

# Configuración de Supabase
SUPA_URL = "https://bijbbbgclsdcyivympop.supabase.co"
SUPA_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJpamJiYmdjbHNkY3lpdnltcG9wIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAwMTM5OTEsImV4cCI6MjA2NTU4OTk5MX0.OnjnkWpJe2khQ03AI97CfNxRi94IGMJQr2trdEKaZCM"
supa = create_client(SUPA_URL, SUPA_KEY)