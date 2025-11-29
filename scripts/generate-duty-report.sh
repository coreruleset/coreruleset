#!/bin/bash

# Currently very agentic script. The idea is to turn it into a small Go program later.
# Script to generate HTML report with recent GitHub issues and PRs
# Usage: ./generate-duty-report.sh <output_html> [days] [reports_dir]
# Examples:
#   ./generate-duty-report.sh ./duty.html              (From last 1 day)
#   ./generate-duty-report.sh ./duty.html 7            (From last 7 days)

OUTPUT_FILE="${1:-"./docs/duty.html"}"
# Default to last 1 day
DAYS="${2:-1}"

# Get script directory for template file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/duty-template.html"

# Check if template file exists
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file not found at $TEMPLATE_FILE"
    exit 1
fi

# Get yesterday's date (for created filter)
if command -v date &> /dev/null; then
    CUTOFF_DATE=$(date -d "$DAYS days ago" +%Y-%m-%d 2>/dev/null || date -v -${DAYS}d +%Y-%m-%d 2>/dev/null)
else
    CUTOFF_DATE=$(date -v -${DAYS}d +%Y-%m-%d)
fi

echo "Fetching data for issues and PRs created in the last $DAYS day(s) (since $CUTOFF_DATE)..."

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo "Error: 'gh' (GitHub CLI) is not installed or not in PATH"
    exit 1
fi

# Fetch recently opened pull requests
echo "Fetching pull requests..."
if ! PRS_JSON=$(gh search prs --created=">=$CUTOFF_DATE" --owner coreruleset --state open --json number,title,url,author,repository --limit 100 2>&1); then
    echo "Error: Failed to fetch pull requests from GitHub"
    echo "Details: $PRS_JSON"
    exit 1
fi
PRS_JSON=$(echo "$PRS_JSON" | jq -c '.')
if [ $? -ne 0 ]; then
    echo "Error: Failed to parse PR JSON response"
    exit 1
fi

# Fetch recently opened issues
echo "Fetching issues..."
if ! ISSUES_JSON=$(gh search issues --created=">=$CUTOFF_DATE" --owner coreruleset --state open --json number,title,url,author,repository --limit 100 2>&1); then
    echo "Error: Failed to fetch issues from GitHub"
    echo "Details: $ISSUES_JSON"
    exit 1
fi
ISSUES_JSON=$(echo "$ISSUES_JSON" | jq -c '.')
if [ $? -ne 0 ]; then
    echo "Error: Failed to parse issues JSON response"
    exit 1
fi

# Get last updates with timestamps
echo "Fetching update timestamps..."
if ! PRS_WITH_UPDATES=$(gh search prs --created=">=$CUTOFF_DATE" --owner coreruleset --state open --json number,repository,updatedAt --limit 100 2>&1); then
    echo "Error: Failed to fetch PR update timestamps"
    echo "Details: $PRS_WITH_UPDATES"
    exit 1
fi
PRS_WITH_UPDATES=$(echo "$PRS_WITH_UPDATES" | jq -r '.[] | "\(.repository.nameWithOwner)\t\(.number)\t\(.updatedAt)"')
if [ $? -ne 0 ]; then
    echo "Error: Failed to parse PR timestamps"
    exit 1
fi

if ! ISSUES_WITH_UPDATES=$(gh search issues --created=">=$CUTOFF_DATE" --owner coreruleset --state open --json number,repository,updatedAt --limit 100 2>&1); then
    echo "Error: Failed to fetch issue update timestamps"
    echo "Details: $ISSUES_WITH_UPDATES"
    exit 1
fi
ISSUES_WITH_UPDATES=$(echo "$ISSUES_WITH_UPDATES" | jq -r '.[] | "\(.repository.nameWithOwner)\t\(.number)\t\(.updatedAt)"')
if [ $? -ne 0 ]; then
    echo "Error: Failed to parse issue timestamps"
    exit 1
fi

# Get current timestamp
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

# Copy template to output
cp "$TEMPLATE_FILE" "$OUTPUT_FILE"

# Escape JSON for embedding
PRS_ESCAPED=$(echo "$PRS_JSON" | sed 's/"/\\"/g' | tr '\n' ' ')
ISSUES_ESCAPED=$(echo "$ISSUES_JSON" | sed 's/"/\\"/g' | tr '\n' ' ')

# Update the HTML file with data and timestamp
sed -i.bak \
    -e "s|{{TIMESTAMP}}|${TIMESTAMP}|g" \
    -e "s|{{DAYS}}|${DAYS}|g" \
    -e "s|{{CUTOFF_DATE}}|${CUTOFF_DATE}|g" \
    -e "s|{{PRS_COUNT}}|$(echo "$PRS_JSON" | jq 'length')|g" \
    -e "s|{{ISSUES_COUNT}}|$(echo "$ISSUES_JSON" | jq 'length')|g" \
    "$OUTPUT_FILE"

# Remove backup file
rm -f "${OUTPUT_FILE}.bak"

# Create temporary file for update times
PRS_UPDATES=$(mktemp)
ISSUES_UPDATES=$(mktemp)

# Store update times in associative array format for lookup
echo "$PRS_WITH_UPDATES" | while IFS=$'\t' read -r repo num time; do
    echo "${repo}#${num}|${time}" >> "$PRS_UPDATES"
done

echo "$ISSUES_WITH_UPDATES" | while IFS=$'\t' read -r repo num time; do
    echo "${repo}#${num}|${time}" >> "$ISSUES_UPDATES"
done

# Create temporary file for table rows
PRS_ROWS=$(mktemp)
ISSUES_ROWS=$(mktemp)

# Function to get update time from file
get_update_time() {
    local updates_file="$1"
    local repo="$2"
    local num="$3"
    grep "^${repo}#${num}|" "$updates_file" 2>/dev/null | cut -d'|' -f2 || echo "N/A"
}

# Generate PR table rows with smart update times
while IFS=$'\n' read -r pr; do
    num=$(echo "$pr" | jq -r '.number')
    title=$(echo "$pr" | jq -r '.title')
    url=$(echo "$pr" | jq -r '.url')
    repo=$(echo "$pr" | jq -r '.repository.nameWithOwner')
    author=$(echo "$pr" | jq -r '.author.login')
    repo_id=$(echo "$repo" | tr '/' '-')
    
    cat >> "$PRS_ROWS" << EOF
            <tr>
                <td><a href="$url" target="_blank">#$num</a></td>
                <td>$title</td>
                <td><a href="https://github.com/$repo" target="_blank">$(echo "$repo" | cut -d'/' -f2)</a></td>
                <td><a href="https://github.com/$author" target="_blank">@$author</a></td>
                <td id="pr-$repo_id-$num">—</td>
            </tr>
EOF
done < <(echo "$PRS_JSON" | jq -c '.[]')

# Generate issues table rows with smart update times
while IFS=$'\n' read -r issue; do
    num=$(echo "$issue" | jq -r '.number')
    title=$(echo "$issue" | jq -r '.title')
    url=$(echo "$issue" | jq -r '.url')
    repo=$(echo "$issue" | jq -r '.repository.nameWithOwner')
    author=$(echo "$issue" | jq -r '.author.login')
    repo_id=$(echo "$repo" | tr '/' '-')
    
    cat >> "$ISSUES_ROWS" << EOF
            <tr>
                <td><a href="$url" target="_blank">#$num</a></td>
                <td>$title</td>
                <td><a href="https://github.com/$repo" target="_blank">$(echo "$repo" | cut -d'/' -f2)</a></td>
                <td><a href="https://github.com/$author" target="_blank">@$author</a></td>
                <td id="issue-$repo_id-$num">—</td>
            </tr>
EOF
done < <(echo "$ISSUES_JSON" | jq -c '.[]')

# Insert PR rows
if [ -s "$PRS_ROWS" ]; then
    if sed --version >/dev/null 2>&1; then
        sed -i "/<tbody id=\"prs-tbody\">/r $PRS_ROWS" "$OUTPUT_FILE"
    else
        sed -i.bak "/<tbody id=\"prs-tbody\">/r $PRS_ROWS" "$OUTPUT_FILE"
        rm -f "${OUTPUT_FILE}.bak"
    fi
fi

# Insert issues rows
if [ -s "$ISSUES_ROWS" ]; then
    if sed --version >/dev/null 2>&1; then
        sed -i "/<tbody id=\"issues-tbody\">/r $ISSUES_ROWS" "$OUTPUT_FILE"
    else
        sed -i.bak "/<tbody id=\"issues-tbody\">/r $ISSUES_ROWS" "$OUTPUT_FILE"
        rm -f "${OUTPUT_FILE}.bak"
    fi
fi

# Create update times script
UPDATE_SCRIPT=$(mktemp)

{
    cat << 'SCRIPT_START'
<script>
(function() {
    // Function to format relative time
    function formatTimeAgo(isoString) {
        const date = new Date(isoString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);
        
        if (seconds < 60) return 'just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + ' minute' + (minutes > 1 ? 's' : '') + ' ago';
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return 'about ' + hours + ' hour' + (hours > 1 ? 's' : '') + ' ago';
        const days = Math.floor(hours / 24);
        return 'about ' + days + ' day' + (days > 1 ? 's' : '') + ' ago';
    }
    
    const prUpdates = {
SCRIPT_START
    
    # Add PR updates - process line by line
    while IFS=$'\t' read -r repo num timestamp; do
        if [ -n "$repo" ] && [ -n "$num" ] && [ -n "$timestamp" ]; then
            printf "        '%s#%s': '%s',\n" "$repo" "$num" "$timestamp"
        fi
    done <<< "$PRS_WITH_UPDATES"
    
    cat << 'SCRIPT_MIDDLE'
    };
    
    const issueUpdates = {
SCRIPT_MIDDLE
    
    # Add issue updates - process line by line
    while IFS=$'\t' read -r repo num timestamp; do
        if [ -n "$repo" ] && [ -n "$num" ] && [ -n "$timestamp" ]; then
            printf "        '%s#%s': '%s',\n" "$repo" "$num" "$timestamp"
        fi
    done <<< "$ISSUES_WITH_UPDATES"
    
    cat << 'SCRIPT_END'
    };
    
    // Update PR times
    Object.keys(prUpdates).forEach(key => {
        const elemId = 'pr-' + key.replace('/', '-').replace('#', '-');
        const elem = document.getElementById(elemId);
        if (elem) elem.textContent = formatTimeAgo(prUpdates[key]);
    });
    
    // Update issue times
    Object.keys(issueUpdates).forEach(key => {
        const elemId = 'issue-' + key.replace('/', '-').replace('#', '-');
        const elem = document.getElementById(elemId);
        if (elem) elem.textContent = formatTimeAgo(issueUpdates[key]);
    });
})();
</script>
SCRIPT_END
} > "$UPDATE_SCRIPT"

# Insert the update script before closing body tag
if sed --version >/dev/null 2>&1; then
    sed -i "/<\/body>/r $UPDATE_SCRIPT" "$OUTPUT_FILE"
else
    sed -i.bak "/<\/body>/r $UPDATE_SCRIPT" "$OUTPUT_FILE"
    rm -f "${OUTPUT_FILE}.bak"
fi

rm -f "$PRS_ROWS" "$ISSUES_ROWS" "$PRS_UPDATES" "$ISSUES_UPDATES" "$UPDATE_SCRIPT"

echo "Duty report generated successfully at $OUTPUT_FILE"
