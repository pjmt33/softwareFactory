cd /Volumes/dbdata/softwareFactory
{
  echo "You are an agent working through Gate 1. You have read readme.md, SKILL.md, and 00-status.md."
  echo "Here is the Gate 1 reference you said you would open:"
  echo "=== references/gate-1-product.md ==="
  cat references/gate-1-product.md
  echo "=== END ==="
  echo ""
  echo "Now begin Gate 1 for first-tracer. Follow the reference exactly."
} | ollama run qwen2.5-coder:3b
