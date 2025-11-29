#!/bin/bash

# Script to generate HTML report from quantitative test results

RESULTS_FILE="$1"
OUTPUT_FILE="$2"
LANGUAGE="$3"
YEAR="$4"
SIZE="$5"
PARANOIA="$6"
COMMIT_SHA="$7"
REPORTS_DIR="$8"  # Directory where individual reports are stored (e.g., gh-pages/reports)

# Get script directory for template file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/report-template.html"

# Extract metrics from JSON
TOTAL_TIME_SECONDS=$(jq -r '.totalTimeSeconds' "$RESULTS_FILE")
TOTAL_TIME_MINUTES=$(printf "%.2f" $(echo "$TOTAL_TIME_SECONDS / 60" | bc -l))
COUNT=$(jq -r '.count' "$RESULTS_FILE")
FALSE_POSITIVES=$(jq -r '.falsePositives' "$RESULTS_FILE")
FP_PER_PARANOIA=$(jq -r '.falsePositivesPerParanoiaLevel | to_entries | map("\(.key): \(.value)") | join(", ")' "$RESULTS_FILE" 2>/dev/null || echo "")
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
DATE=$(date -u +"%Y-%m-%d")
TIME=$(date -u +"%H%M%S")

# Generate unique report filename based on date, time and commit
REPORT_FILENAME="${DATE}_${TIME}_${COMMIT_SHA:0:8}.json"
REPORT_PATH="${REPORTS_DIR}/${REPORT_FILENAME}"

# Create reports directory if it doesn't exist
mkdir -p "${REPORTS_DIR}"

# Extract FP per paranoia level
FP_PL1=$(jq -r '.falsePositivesPerParanoiaLevel."1" // 0' "$RESULTS_FILE")
FP_PL2=$(jq -r '.falsePositivesPerParanoiaLevel."2" // 0' "$RESULTS_FILE")
FP_PL3=$(jq -r '.falsePositivesPerParanoiaLevel."3" // 0' "$RESULTS_FILE")
FP_PL4=$(jq -r '.falsePositivesPerParanoiaLevel."4" // 0' "$RESULTS_FILE")

# Track previous values for each PL
PREVIOUS_FP_PL1=0
PREVIOUS_FP_PL2=0
PREVIOUS_FP_PL3=0
PREVIOUS_FP_PL4=0

# Read previous false positives and report path if file exists
# IMPORTANT: Find previous report BEFORE copying the new one
PREVIOUS_FP=0
PREVIOUS_REPORT=""
FP_DIFF=0
FP_COLOR="grey"
FP_SYMBOL="="
DIFF_FILE=""
DIFF_OUTPUT=""

if [ -f "$OUTPUT_FILE" ] && [ -d "$REPORTS_DIR" ]; then
    # Find the most recent report file
    PREVIOUS_REPORT=$(ls -t "$REPORTS_DIR"/*.json 2>/dev/null | head -1)
    
    if [ -n "$PREVIOUS_REPORT" ] && [ -f "$PREVIOUS_REPORT" ]; then
        # Extract previous FP values per PL
        PREVIOUS_FP_PL1=$(jq -r '.falsePositivesPerParanoiaLevel."1" // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL2=$(jq -r '.falsePositivesPerParanoiaLevel."2" // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL3=$(jq -r '.falsePositivesPerParanoiaLevel."3" // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL4=$(jq -r '.falsePositivesPerParanoiaLevel."4" // 0' "$PREVIOUS_REPORT")
        
        # Extract previous total FP
        PREVIOUS_FP=$(jq -r '.falsePositives' "$PREVIOUS_REPORT")
        
        # Create diff between old and new results
        DIFF_OUTPUT=$(diff <(jq . "$PREVIOUS_REPORT") <(jq . "$RESULTS_FILE") || true)
    fi
fi

# NOW copy the results file to the reports directory (after finding previous)
cp "$RESULTS_FILE" "$REPORT_PATH"

FP_DIFF=$((FALSE_POSITIVES - PREVIOUS_FP))
PL1_DIFF=$((FP_PL1 - PREVIOUS_FP_PL1))
PL2_DIFF=$((FP_PL2 - PREVIOUS_FP_PL2))
PL3_DIFF=$((FP_PL3 - PREVIOUS_FP_PL3))
PL4_DIFF=$((FP_PL4 - PREVIOUS_FP_PL4))

# Set color and display for main FPchange value
get_change_display() {
    local diff=$1
    if [ "$diff" -gt 0 ]; then
        echo "change-increase|▲ +${diff}"
    elif [ "$diff" -lt 0 ]; then
        echo "change-decrease|▼ ${diff}"
    else
        echo "change-same|= 0"
    fi
}

# Calculate changes for each PL

# Set color and display for main FP
if [ $FP_DIFF -gt 0 ]; then
    FP_COLOR="change-increase"
    FP_DISPLAY="▲ +${FP_DIFF}"
elif [ $FP_DIFF -lt 0 ]; then
    FP_COLOR="change-decrease"
    FP_DISPLAY="▼ ${FP_DIFF}"
else
    FP_COLOR="change-same"
    FP_DISPLAY="= 0"
fi

# Get display for each PL
PL1_DATA=$(get_change_display $PL1_DIFF)
PL1_COLOR="${PL1_DATA%|*}"
PL1_DISPLAY="${PL1_DATA#*|}"

PL2_DATA=$(get_change_display $PL2_DIFF)
PL2_COLOR="${PL2_DATA%|*}"
PL2_DISPLAY="${PL2_DATA#*|}"

PL3_DATA=$(get_change_display $PL3_DIFF)
PL3_COLOR="${PL3_DATA%|*}"
PL3_DISPLAY="${PL3_DATA#*|}"

PL4_DATA=$(get_change_display $PL4_DIFF)
PL4_COLOR="${PL4_DATA%|*}"
PL4_DISPLAY="${PL4_DATA#*|}"

# Check if HTML file exists
if [ ! -f "$OUTPUT_FILE" ]; then
    # Create new HTML file from template
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "Error: Template file not found at $TEMPLATE_FILE"
        exit 1
    fi
    
    # Read template and replace placeholders
    sed -e "s/{{TIMESTAMP}}/${TIMESTAMP}/g" \
        -e "s/{{LANGUAGE}}/${LANGUAGE}/g" \
        -e "s/{{YEAR}}/${YEAR}/g" \
        -e "s/{{SIZE}}/${SIZE}/g" \
        -e "s/{{PARANOIA}}/${PARANOIA}/g" \
        "$TEMPLATE_FILE" > "$OUTPUT_FILE"
else
    # File exists, insert new row after tbody tag (cross-platform compatible)
    if sed --version >/dev/null 2>&1; then
        # GNU sed (Linux)
        sed -i '/<tbody>/a <!-- NEW_ROW -->' "$OUTPUT_FILE"
    else
        # BSD sed (macOS)
        sed -i.bak '/<tbody>/a\
<!-- NEW_ROW -->
' "$OUTPUT_FILE" && rm -f "$OUTPUT_FILE.bak"
    fi
fi

# Create unique row ID based on date, time and commit
ROW_ID="${DATE}_${TIME}_${COMMIT_SHA:0:8}"

# Build paranoia level table rows
FP_PARANOIA_TABLE=""
if [ -n "$FP_PER_PARANOIA" ]; then
    while IFS=': ' read -r level count; do
        FP_PARANOIA_TABLE="$(printf "%b" "${FP_PARANOIA_TABLE}                            <tr><td>${level}</td><td>${count}</td></tr>\n")"
    done < <(echo "$FP_PER_PARANOIA" | sed 's/, /\n/g')
fi

# Escape diff output for HTML
DIFF_HTML=""
if [ -n "$DIFF_OUTPUT" ]; then
    DIFF_HTML=$(printf '%s\n' "$DIFF_OUTPUT" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/"/\&quot;/g')
fi

{
cat <<EOF
            <tr>
                <td>${DATE}</td>
                <td><a href="https://github.com/coreruleset/coreruleset/commit/${COMMIT_SHA}" target="_blank"><code>${COMMIT_SHA:0:8}</code></a></td>
                <td>${TOTAL_TIME_MINUTES} min</td>
                <td>${FALSE_POSITIVES}</td>
                <td class="${FP_COLOR}">${FP_DISPLAY}</td>
                <td class="${PL1_COLOR}">${PL1_DISPLAY}</td>
                <td class="${PL2_COLOR}">${PL2_DISPLAY}</td>
                <td class="${PL3_COLOR}">${PL3_DISPLAY}</td>
                <td class="${PL4_COLOR}">${PL4_DISPLAY}</td>
                <td><a href="javascript:void(0);" id="link-${ROW_ID}" onclick="toggleDetails('${ROW_ID}'); return false;">Show</a></td>
                <td><a href="reports/${REPORT_FILENAME}" target="_blank">📄</a></td>
            </tr>
            <tr id="details-${ROW_ID}" class="details-row">
                <td colspan="11" class="details-cell">
                    <h3>Diff from Previous Run</h3>
EOF

if [ -n "$DIFF_HTML" ]; then
    printf '                    <div class="diff-content">%s</div>\n' "$DIFF_HTML"
else
    printf '                    <p><em>No previous run available for comparison</em></p>\n'
fi

cat <<EOF
                </td>
            </tr>
EOF
} > /tmp/new_row.txt

# Update embedded report data
# Extract current report data, add new report, and update
if [ -f "$OUTPUT_FILE" ]; then
    # Extract existing report data - get everything between the script tags
    EXISTING_DATA=$(awk '/<script id="report-data"/ {flag=1; next} /<\/script>/ {flag=0} flag' "$OUTPUT_FILE" | tr -d '\n' | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')
    
    # Create new report entry with date, time, and data
    NEW_REPORT_ENTRY=$(cat "$REPORT_PATH" | jq -c ". + {date: \"${DATE}\", time: \"${TIME}\", timestamp: \"${DATE} ${TIME:0:2}:${TIME:2:2}\"}")
    
    # If existing data is empty array or empty, replace with new array containing one item
    if [ "$EXISTING_DATA" = "[]" ] || [ -z "$EXISTING_DATA" ]; then
        NEW_DATA="[$NEW_REPORT_ENTRY]"
    else
        # Add new report to existing array - check if it's valid JSON first
        if echo "$EXISTING_DATA" | jq empty 2>/dev/null; then
            NEW_DATA=$(echo "$EXISTING_DATA" | jq -c ". + [$NEW_REPORT_ENTRY]")
        else
            # Invalid JSON, start fresh
            NEW_DATA="[$NEW_REPORT_ENTRY]"
        fi
    fi
    
    # Create a temporary file with the updated JSON
    TMP_FILE=$(mktemp)
    awk -v new_data="    $NEW_DATA" '
        /<script id="report-data"/ {
            print
            print new_data
            in_script=1
            next
        }
        /<\/script>/ && in_script {
            in_script=0
        }
        !in_script
    ' "$OUTPUT_FILE" > "$TMP_FILE"
    mv "$TMP_FILE" "$OUTPUT_FILE"
fi

if [ -f "$OUTPUT_FILE" ] && grep -q "<!-- NEW_ROW -->" "$OUTPUT_FILE"; then
    # Replace placeholder with new row using awk for better compatibility
    awk '
        /<!-- NEW_ROW -->/ {
            while ((getline line < "/tmp/new_row.txt") > 0) {
                print line
            }
            next
        }
        { print }
    ' "$OUTPUT_FILE" > "$OUTPUT_FILE.tmp" && mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"
    rm -f /tmp/new_row.txt
else
    # Append to new file
    cat /tmp/new_row.txt >> "$OUTPUT_FILE"
    cat <<EOF >> "$OUTPUT_FILE"
        </tbody>
    </table>
</body>
</html>
EOF
    rm -f /tmp/new_row.txt
fi
