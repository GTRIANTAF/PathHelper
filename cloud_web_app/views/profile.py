import streamlit as st
from profile_manager import load_scenarios

def render():
    st.markdown("### Αποθηκευμένα Σενάρια")
    saved_scenarios = load_scenarios()
    
    if saved_scenarios:
        for name, data in saved_scenarios.items():
            with st.container():
                st.markdown(f"#### {name}")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Τύπος Κατεύθυνσης:** {data.get('scenario_type')}")
                    valid_text = 'Έγκυρο Πρόγραμμα' if data.get('valid') else 'Μη Έγκυρο Πρόγραμμα'
                    st.write(f"**Κατάσταση:** {valid_text}")
                    st.write(f"**Επιλεγμένα Μαθήματα:** {len(data.get('my_electives', []))}")
                with col2:
                    if st.button("Φόρτωση στον Checker", key=f"load_{name}", use_container_width=True):
                        st.session_state.loaded_scenario = data
                        st.session_state.check_performed = False
                        st.session_state.current_page = "checker"
                        st.rerun()
                st.divider()
    else:
        st.info("Δεν υπάρχουν αποθηκευμένα σενάρια ακόμα. Πηγαίνετε στον Path Checker για να δημιουργήσετε ένα!")
