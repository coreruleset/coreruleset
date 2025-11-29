#!/bin/bash

# Script to generate HTML report from quantitative test results
# Usage: ./update-quant-weekly-report.sh [--rebuild] <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir> [results_file]
# 
# Normal mode: ./update-quant-weekly-report.sh <results_file> <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>
# Rebuild mode: ./update-quant-weekly-report.sh --rebuild <output_html> <language> <year> <size> <paranoia> <commit_sha> <reports_dir>

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# Generate change display for a diff value
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

# Extract metrics from a JSON report file
extract_metrics() {
    local report_file="$1"
    
    jq -r '. as $root | {
        false_positives: .falsePositives,
        fp_pl1: (.falsePositivesPerParanoiaLevel["1"] // 0),
        fp_pl2: (.falsePositivesPerParanoiaLevel["2"] // 0),
        fp_pl3: (.falsePositivesPerParanoiaLevel["3"] // 0),
        fp_pl4: (.falsePositivesPerParanoiaLevel["4"] // 0),
        total_time_seconds: .totalTimeSeconds,
        date: .date,
        timestamp: .timestamp,
        commit: (.commit // "unknown")
    }' "$report_file"
}

# Generate a table row HTML for a given report
generate_table_row() {
    local row_id="$1"
    local filename="$2"
    local date="$3"
    local commit_full="$4"
    local commit_short="$5"
    local total_time_minutes="$6"
    local false_positives="$7"
    local fp_color="$8"
    local fp_display="$9"
    local pl1_color="${10}"
    local pl1_display="${11}"
    local pl2_color="${12}"
    local pl2_display="${13}"
    local pl3_color="${14}"
    local pl3_display="${15}"
    local pl4_color="${16}"
    local pl4_display="${17}"
    local diff_output="${18}"
    
    cat << EOF
            <tr>
                <td>$date</td>
                <td><a href="https://github.com/coreruleset/coreruleset/commit/${commit_full}" target="_blank"><code>${commit_short}</code></a></td>
                <td>${total_time_minutes} min</td>
                <td>${false_positives}</td>
                <td class="${fp_color}">${fp_display}</td>
                <td class="${pl1_color}">${pl1_display}</td>
                <td class="${pl2_color}">${pl2_display}</td>
                <td class="${pl3_color}">${pl3_display}</td>
                <td class="${pl4_color}">${pl4_display}</td>
                <td><a href="javascript:void(0);" id="link-${row_id}" onclick="toggleDetails('${row_id}'); return false;">Show</a></td>
                <td><a href="reports/${filename}" target="_blank">📄</a></td>
            </tr>
            <tr id="details-${row_id}" class="details-row">
                <td colspan="11" class="details-cell">
                    <h3>Diff from Previous Run</h3>
EOF
    
    if [ -z "$diff_output" ]; then
        cat << EOF
                    <p><em>No previous run available for comparison</em></p>
EOF
    else
        cat << EOF
                    <div class="diff-content">${diff_output}</div>
EOF
    fi
    
    cat << EOF
                </td>
            </tr>
EOF
}

# ============================================================================
# MAIN SCRIPT
# ============================================================================

REBUILD_MODE=false

# Check for --rebuild flag
if [ "$1" = "--rebuild" ]; then
    REBUILD_MODE=true
    OUTPUT_FILE="$2"
    LANGUAGE="$3"
    YEAR="$4"
    SIZE="$5"
    PARANOIA="$6"
    COMMIT_SHA="$7"
    REPORTS_DIR="$8"
else
    RESULTS_FILE="$1"
    OUTPUT_FILE="$2"
    LANGUAGE="$3"
    YEAR="$4"
    SIZE="$5"
    PARANOIA="$6"
    COMMIT_SHA="$7"
    REPORTS_DIR="$8"
fi

# Get script directory for template file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_FILE="${SCRIPT_DIR}/report-template.html"

if [ "$REBUILD_MODE" = true ]; then
    # REBUILD MODE: Read all reports from directory and regenerate everything
    echo "Rebuild mode: Regenerating report from all reports in $REPORTS_DIR"
    
    # Check if reports directory exists
    if [ ! -d "$REPORTS_DIR" ]; then
        echo "Error: Reports directory not found at $REPORTS_DIR"
        exit 1
    fi
    
    # Check if template file exists
    if [ ! -f "$TEMPLATE_FILE" ]; then
        echo "Error: Template file not found at $TEMPLATE_FILE"
        exit 1
    fi
    
    # Get current timestamp
    TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    
    # Create new HTML file from template with placeholders
    sed -e "s/{{TIMESTAMP}}/${TIMESTAMP}/g" \
        -e "s/{{LANGUAGE}}/${LANGUAGE}/g" \
        -e "s/{{YEAR}}/${YEAR}/g" \
        -e "s/{{SIZE}}/${SIZE}/g" \
        -e "s/{{PARANOIA}}/${PARANOIA}/g" \
        "$TEMPLATE_FILE" > "$OUTPUT_FILE"
    
    # Collect all report files, sorted by date_time
    REPORT_FILES=($(ls -1 "$REPORTS_DIR"/*.json 2>/dev/null | sort))
    
    if [ ${#REPORT_FILES[@]} -eq 0 ]; then
        echo "No reports found in $REPORTS_DIR"
        exit 0
    fi
    
    echo "Found ${#REPORT_FILES[@]} reports to process"
    
    # Build JSON array from all reports
    JSON_ARRAY="["
    FIRST=true
    for REPORT_FILE in "${REPORT_FILES[@]}"; do
        if [ "$FIRST" = true ]; then
            JSON_ARRAY="${JSON_ARRAY}$(cat "$REPORT_FILE")"
            FIRST=false
        else
            JSON_ARRAY="${JSON_ARRAY},$(cat "$REPORT_FILE")"
        fi
    done
    JSON_ARRAY="${JSON_ARRAY}]"
    
    # Validate JSON
    if ! echo "$JSON_ARRAY" | jq . >/dev/null 2>&1; then
        echo "Error: Invalid JSON generated"
        exit 1
    fi
    
    # Update the embedded JSON data in the HTML file using awk
    awk -v json_data="$JSON_ARRAY" '
        /<script id="report-data"/ {
            print $0
            getline
            next
        }
        /<\/script>/ && flag {
            print "    " json_data
            print $0
            flag=0
            next
        }
        { print $0 }
        /<script id="report-data"/ { flag=1 }
    ' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    
    # Generate table rows for each report
    ROWS_FILE=$(mktemp)
    PREVIOUS_FP=0
    PREVIOUS_PL1=0
    PREVIOUS_PL2=0
    PREVIOUS_PL3=0
    PREVIOUS_PL4=0
    PREVIOUS_REPORT=""
    
    for REPORT_FILE in "${REPORT_FILES[@]}"; do
        FILENAME=$(basename "$REPORT_FILE")
        ROW_ID="${FILENAME%.json}"
        
        # Extract metrics using jq
        METRICS=$(extract_metrics "$REPORT_FILE")
        FALSE_POSITIVES=$(echo "$METRICS" | jq -r '.false_positives')
        FP_PL1=$(echo "$METRICS" | jq -r '.fp_pl1')
        FP_PL2=$(echo "$METRICS" | jq -r '.fp_pl2')
        FP_PL3=$(echo "$METRICS" | jq -r '.fp_pl3')
        FP_PL4=$(echo "$METRICS" | jq -r '.fp_pl4')
        TOTAL_TIME_SECONDS=$(echo "$METRICS" | jq -r '.total_time_seconds')
        DATE=$(echo "$METRICS" | jq -r '.date')
        COMMIT_FULL=$(echo "$METRICS" | jq -r '.commit')
        COMMIT_SHORT="${COMMIT_FULL:0:8}"
        TOTAL_TIME_MINUTES=$(printf "%.2f" $(echo "$TOTAL_TIME_SECONDS / 60" | bc -l))
        
        # Calculate diffs
        FP_DIFF=$((FALSE_POSITIVES - PREVIOUS_FP))
        PL1_DIFF=$((FP_PL1 - PREVIOUS_PL1))
        PL2_DIFF=$((FP_PL2 - PREVIOUS_PL2))
        PL3_DIFF=$((FP_PL3 - PREVIOUS_PL3))
        PL4_DIFF=$((FP_PL4 - PREVIOUS_PL4))
        
        # Get display strings
        FP_DATA=$(get_change_display $FP_DIFF)
        FP_COLOR="${FP_DATA%|*}"
        FP_DISPLAY="${FP_DATA#*|}"
        
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
        
        # Generate diff if we have a previous report
        DIFF_OUTPUT=""
        if [ -n "$PREVIOUS_REPORT" ]; then
            DIFF_OUTPUT=$(diff <(jq . "$PREVIOUS_REPORT") <(jq . "$REPORT_FILE") || true)
        fi
        
        # Generate and write table row
        generate_table_row "$ROW_ID" "$FILENAME" "$DATE" "$COMMIT_FULL" "$COMMIT_SHORT" \
            "$TOTAL_TIME_MINUTES" "$FALSE_POSITIVES" "$FP_COLOR" "$FP_DISPLAY" \
            "$PL1_COLOR" "$PL1_DISPLAY" "$PL2_COLOR" "$PL2_DISPLAY" \
            "$PL3_COLOR" "$PL3_DISPLAY" "$PL4_COLOR" "$PL4_DISPLAY" \
            "$DIFF_OUTPUT" >> "$ROWS_FILE"
        
        # Update previous values
        PREVIOUS_FP=$FALSE_POSITIVES
        PREVIOUS_PL1=$FP_PL1
        PREVIOUS_PL2=$FP_PL2
        PREVIOUS_PL3=$FP_PL3
        PREVIOUS_PL4=$FP_PL4
        PREVIOUS_REPORT="$REPORT_FILE"
    done
    
    # Insert all rows into HTML
    if sed --version >/dev/null 2>&1; then
        sed -i "/<tbody>/r $ROWS_FILE" "$OUTPUT_FILE"
    else
        sed -i.bak "/<tbody>/r $ROWS_FILE" "$OUTPUT_FILE"
        rm -f "${OUTPUT_FILE}.bak"
    fi
    
    rm -f "$ROWS_FILE"
    
    echo "Report regenerated successfully at $OUTPUT_FILE"
    exit 0
fi

# NORMAL MODE: Add single result

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

# Read previous false positives and report path if file exists
# IMPORTANT: Find previous report BEFORE copying the new one
PREVIOUS_FP=0
PREVIOUS_FP_PL1=0
PREVIOUS_FP_PL2=0
PREVIOUS_FP_PL3=0
PREVIOUS_FP_PL4=0
PREVIOUS_REPORT=""
DIFF_OUTPUT=""

if [ -f "$OUTPUT_FILE" ] && [ -d "$REPORTS_DIR" ]; then
    # Find the most recent report file
    PREVIOUS_REPORT=$(ls -t "$REPORTS_DIR"/*.json 2>/dev/null | head -1)
    
    if [ -n "$PREVIOUS_REPORT" ] && [ -f "$PREVIOUS_REPORT" ]; then
        # Extract previous FP values per PL
        PREVIOUS_FP_PL1=$(jq -r '.falsePositivesPerParanoiaLevel["1"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL2=$(jq -r '.falsePositivesPerParanoiaLevel["2"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL3=$(jq -r '.falsePositivesPerParanoiaLevel["3"] // 0' "$PREVIOUS_REPORT")
        PREVIOUS_FP_PL4=$(jq -r '.falsePositivesPerParanoiaLevel["4"] // 0' "$PREVIOUS_REPORT")
        
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

# Get display strings for each metric using helper function
FP_DATA=$(get_change_display $FP_DIFF)
FP_COLOR="${FP_DATA%|*}"
FP_DISPLAY="${FP_DATA#*|}"

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
