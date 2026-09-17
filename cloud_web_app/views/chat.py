import streamlit as st
import json
import os
import sys
from knowledge_base import CEID_COURSES
from connector import get_ai_response
from mcp_client import StreamlitMCPClient

def render():
    if "mcp_client" not in st.session_state:
        import time
        # Create a placeholder for the cool animation
        loading_placeholder = st.empty()
        
        import streamlit.components.v1 as components

        html_code = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #050914; overflow: hidden; cursor: crosshair; }
                #aurora-canvas { display: block; width: 100%; height: 100%; }
                .hud { position: absolute; top: 20px; left: 20px; display: flex; align-items: center; gap: 8px; pointer-events: none; user-select: none; }
                .ping { width: 8px; height: 8px; border-radius: 50%; background: #00f2fe; animation: ping 1s cubic-bezier(0, 0, 0.2, 1) infinite; }
                .text { font-size: 12px; font-family: monospace; letter-spacing: 2px; color: rgba(0, 242, 254, 0.8); }
                @keyframes ping { 75%, 100% { transform: scale(2); opacity: 0; } }
            </style>
        </head>
        <body>
            <canvas id="aurora-canvas"></canvas>
            <div class="hud">
                <span class="ping"></span>
                <span class="text">AURA ENGINE</span>
            </div>
            <script>
                // Streamlit isolates components in an iframe. 
                // Since this is a srcdoc iframe, it's same-origin! We can access the parent DOM to make the iframe fullscreen!
                try {
                    const parentDoc = window.parent.document;
                    const iframes = parentDoc.querySelectorAll('iframe');
                    iframes.forEach(iframe => {
                        if (iframe.contentWindow === window) {
                            iframe.style.position = 'fixed';
                            iframe.style.top = '0';
                            iframe.style.left = '0';
                            iframe.style.width = '100vw';
                            iframe.style.height = '100vh';
                            iframe.style.zIndex = '2147483647';
                            iframe.style.border = 'none';
                        }
                    });
                } catch(e) {
                    console.error("Could not make iframe fullscreen", e);
                }

                const canvas = document.getElementById('aurora-canvas');
                const ctx = canvas.getContext('2d');
                
                let width = window.innerWidth;
                let height = window.innerHeight;
                canvas.width = width;
                canvas.height = height;

                window.addEventListener('resize', () => {
                    width = window.innerWidth;
                    height = window.innerHeight;
                    canvas.width = width;
                    canvas.height = height;
                });

                const mouse = { x: -1000, y: -1000, targetX: -1000, targetY: -1000 };
                window.addEventListener('mousemove', (e) => {
                    mouse.targetX = e.clientX;
                    mouse.targetY = e.clientY;
                });
                window.addEventListener('mouseleave', () => {
                    mouse.targetX = -1000;
                    mouse.targetY = -1000;
                });

                const speed = 0.8;
                const amplitude = 80;
                const glowStrength = 30;
                const lineCount = 5;

                let time = 0;
                
                const particles = Array.from({ length: 30 }, () => ({
                  x: Math.random() * width,
                  y: Math.random() * height,
                  size: Math.random() * 2 + 0.5,
                  speed: Math.random() * 0.3 + 0.1,
                  alpha: Math.random() * 0.5 + 0.1,
                  angle: Math.random() * Math.PI * 2,
                }));

                function render() {
                  time += speed * 0.008;

                  mouse.x += (mouse.targetX - mouse.x) * 0.08;
                  mouse.y += (mouse.targetY - mouse.y) * 0.08;

                  ctx.fillStyle = '#050914';
                  ctx.fillRect(0, 0, width, height);

                  particles.forEach(p => {
                    p.angle += 0.002;
                    p.x += Math.cos(p.angle) * p.speed;
                    p.y -= p.speed;

                    if (p.y < 0) p.y = height;
                    if (p.x < 0 || p.x > width) p.x = Math.random() * width;

                    ctx.beginPath();
                    ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                    ctx.fillStyle = `rgba(0, 242, 254, ${p.alpha})`;
                    ctx.fill();
                  });

                  ctx.save();
                  ctx.shadowBlur = glowStrength;
                  ctx.shadowColor = 'rgba(0, 242, 254, 0.5)';

                  for (let i = 0; i < lineCount; i++) {
                    const ratio = i / lineCount;
                    const waveTime = time + (i * 0.35);

                    ctx.beginPath();

                    const gradient = ctx.createLinearGradient(0, height, width, 0);
                    gradient.addColorStop(0, '#00f2fe');
                    gradient.addColorStop(0.5, '#4facfe');
                    gradient.addColorStop(1, '#7f00ff');

                    ctx.strokeStyle = gradient;
                    ctx.lineWidth = 3.5 * (1.2 - ratio * 0.8);
                    ctx.globalAlpha = 0.2 + (1 - ratio) * 0.6;
                    ctx.globalCompositeOperation = 'screen';

                    for (let x = 0; x <= width; x += 4) {
                      const xNorm = x / width;
                      const envelope = Math.sin(xNorm * Math.PI);

                      const wave1 = Math.sin(xNorm * Math.PI * 1.5 + waveTime);
                      const wave2 = Math.cos(xNorm * Math.PI * 2.5 - waveTime * 0.8);

                      const diagonalBaseY = height * (1.0 - xNorm) * 0.8 + (height * 0.1);
                      let y = diagonalBaseY + (wave1 * amplitude * 0.7 * envelope) + (wave2 * amplitude * 0.3 * envelope);

                      const dx = x - mouse.x;
                      const dy = y - mouse.y;
                      const distance = Math.sqrt(dx * dx + dy * dy);
                      if (distance < 150) {
                        const force = (1 - distance / 150);
                        y += (dy > 0 ? 1 : -1) * force * 50 * envelope;
                      }

                      if (x === 0) {
                        ctx.moveTo(x, y);
                      } else {
                        ctx.lineTo(x, y);
                      }
                    }
                    ctx.stroke();
                  }
                  ctx.restore();

                  requestAnimationFrame(render);
                }
                render();
            </script>
        </body>
        </html>
        """

        with loading_placeholder:
            components.html(html_code, height=600)

        server_path = os.path.join(os.path.dirname(__file__), "..", "ceid_mcp_server.py")
        st.session_state.mcp_client = StreamlitMCPClient(
            command=sys.executable,
            args=[server_path]
        )
        try:
            st.session_state.mcp_tools = st.session_state.mcp_client.get_tools()
            time.sleep(1.5) # Allow the user to see the cool animation briefly before it clears!
        except Exception as e:
            st.error(f"Failed to load MCP tools: {e}")
            st.session_state.mcp_tools = None
            
        # Clear the animation once loading is complete
        loading_placeholder.empty()

    st.sidebar.markdown("### My Progress")
    st.markdown("**Ανέβασμα Δεδομένων**")
    uploaded_file = st.file_uploader("Upload my_grades.json", type=["json"])

    if "user_grades" not in st.session_state:
        st.session_state.user_grades = []

    if uploaded_file is not None:
        try:
            grades_data = json.load(uploaded_file)
            st.session_state.user_grades = grades_data
            st.success(f"Φορτώθηκαν {len(grades_data)} περασμένα μαθήματα!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # 1. Κατασκευή του Knowledge Base String (RAG)
    available_courses_str = "AVAILABLE COURSES PER DIRECTION:\n"
    for direction, groups in CEID_COURSES.items():
        available_courses_str += f"\nDirection: {direction}\n"
        for group, courses in groups.items():
            available_courses_str += f" - {group}: {', '.join(courses.keys())}\n"

    # 2. Οι Αγαπημένοι σου Base Rules
    base_rules = f"""
    You are the official Academic Advisor for the Computer Engineering & Informatics Department (CEID) at the University of Patras.

    CRITICAL INSTRUCTION 1: Process all your reasoning and rules in English to avoid mistakes, but YOUR FINAL REPLY TO THE STUDENT MUST BE IN NATURAL GREEK.
    CRITICAL INSTRUCTION 2: NEVER invent, translate, or hallucinate course names. ONLY recommend exact course names from the "AVAILABLE COURSES" list provided below.

    Degree Rules:
    - 17 elective courses total (11 in Winter semesters, 6 in Spring).
    - Basic Rule (MANDATORY): At least 1 course from K1 (Theory), at least 1 from K2, K3, or K4 (Hardware/Networks), and at least 1 from K5 or K6 (Software).
    - 3 Scenarios: 
      1) One Main Direction: 5 Group A, 5 Group B, 5 Group A of other directions, 2 free.
      2) Two Main: 5A+2B (first dir), 5A+2B (second dir), 3 free.
      3) General: 10 Group A (across all), 7 free.

    {available_courses_str}
    """

    # 3. Δυναμική Ενσωμάτωση Βαθμών
    if st.session_state.user_grades and len(st.session_state.user_grades) > 0:
        passed_names = []
        for item in st.session_state.user_grades:
            name = item.get("name", "")
            grade_val = str(item.get("grade", "0")).replace(",", ".")
            try:
                if float(grade_val) >= 5.0:
                    passed_names.append(name)
            except:
                continue

        passed_courses_str = ", ".join(passed_names)
        system_context = base_rules + f"\n\nSTUDENT'S PROGRESS: The student has already passed: [{passed_courses_str}]. DO NOT suggest these. Use them only to understand their profile."
    else:
        system_context = base_rules + "\n\nATTENTION: The student HAS NOT uploaded grades yet. Ask them to upload their JSON for personalized help."

    # 4. Διαχείριση Ιστορικού
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": system_context},
            {"role": "assistant",
             "content": "Γεια σου! Είμαι ο AI Advisor του CEID. Πώς μπορώ να σε βοηθήσω με την επιλογή των μαθημάτων σου;"}
        ]
    else:
        st.session_state.chat_history[0]["content"] = system_context

    # 5. Εμφάνιση μηνυμάτων
    for message in st.session_state.chat_history:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 6. Chat Input
    if user_input := st.chat_input("Ρώτησε κάτι τον Advisor..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Ο Advisor αναλύει το πρόγραμμα σπουδών..."):
                bot_reply = get_ai_response(
                    st.session_state.chat_history,
                    mcp_client=st.session_state.get("mcp_client"),
                    tools=st.session_state.get("mcp_tools")
                )
                st.markdown(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
