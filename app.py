"""
Social Mood Matcher - AI Caption & Hashtag Generator
Main Streamlit application for generating AI-powered social media captions.

Author: Senior Generative AI Engineer
Version: 1.0.0
"""

import streamlit as st
from PIL import Image
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import UI_CONFIG, CAPTION_STYLES, CHARACTER_LIMITS, USE_GEMINI, API_KEYS
from utils.image_utils import validate_and_load_image, ImageProcessor
from utils.text_utils import combine_caption_and_hashtags
from services.image_sentiment import get_sentiment_detector
from services.caption_generator import get_caption_generator
from services.hashtag_engine import get_hashtag_engine
from services.character_limiter import get_character_limiter
from services.gemini_service import get_gemini_analyzer


# Page configuration
st.set_page_config(
    page_title=UI_CONFIG["page_title"],
    page_icon=UI_CONFIG["page_icon"],
    layout=UI_CONFIG["layout"],
    initial_sidebar_state=UI_CONFIG["initial_sidebar_state"]
)

# Custom CSS for enhanced visibility and modern UI
st.markdown("""
<style>    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.3rem;
        margin-bottom: 2.5rem;
        font-weight: 500;
    }
    
    /* Sentiment badge with better contrast */
    .sentiment-badge {
        display: inline-block;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 800;
        font-size: 1.4rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .confidence-score {
        font-size: 1.1rem;
        font-weight: 600;
        margin-left: 0.8rem;
        opacity: 0.9;
    }
    
    /* Caption box with high contrast */
    .caption-box {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 3px solid #667eea;
        margin: 1.5rem 0;
        font-size: 1.4rem;
        line-height: 1.8;
        color: #1a1a1a;
        font-weight: 600;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    /* Hashtag box with better visibility */
    .hashtag-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        color: #0d47a1;
        font-weight: 700;
        font-size: 1.3rem;
        border: 2px solid #2196f3;
        box-shadow: 0 6px 20px rgba(33, 150, 243, 0.2);
    }
    
    /* Character counter with clear colors */
    .char-counter {
        text-align: right;
        font-size: 1.1rem;
        margin-top: 1rem;
        font-weight: 700;
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .char-ok {
        color: #ffffff;
        background-color: #28a745;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    .char-warning {
        color: #000000;
        background-color: #ffc107;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    .char-danger {
        color: #ffffff;
        background-color: #dc3545;
        padding: 0.5rem 1rem;
        border-radius: 8px;
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        font-weight: 800;
        border: none;
        padding: 1rem;
        border-radius: 12px;
        font-size: 1.2rem;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Info cards */
    .info-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 5px solid #667eea;
    }
    
    /* Section headers */
    h3 {
        color: #333;
        font-weight: 700;
        font-size: 1.8rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Streamlit native elements */
    .stMarkdown {
        font-size: 1.1rem;
    }
    
    /* Code block for copy */
    .stCodeBlock {
        background-color: #f5f5f5 !important;
        border: 2px solid #ddd !important;
        border-radius: 10px !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    /* Success/Info/Warning boxes */
    .stSuccess, .stInfo, .stWarning {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 1rem !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)





def initialize_session_state():
    """Initialize session state variables."""
    if 'sentiment_result' not in st.session_state:
        st.session_state.sentiment_result = None
    if 'generated_caption' not in st.session_state:
        st.session_state.generated_caption = None
    if 'generated_hashtags' not in st.session_state:
        st.session_state.generated_hashtags = None
    if 'selected_style' not in st.session_state:
        st.session_state.selected_style = 'casual'
    if 'models_loaded' not in st.session_state:
        st.session_state.models_loaded = False
    if 'use_gemini' not in st.session_state:
        st.session_state.use_gemini = USE_GEMINI
    if 'gemini_analyzer' not in st.session_state:
        st.session_state.gemini_analyzer = None
    if 'caption_variants' not in st.session_state:
        st.session_state.caption_variants = {}
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'visual_analysis' not in st.session_state:
        st.session_state.visual_analysis = None


@st.cache_resource
def load_models():
    """Load AI models (cached to avoid reloading)."""
    with st.spinner("Loading AI models... This may take a minute on first run."):
        detector = get_sentiment_detector()
        generator = get_caption_generator()
        hashtag_engine = get_hashtag_engine()
        limiter = get_character_limiter()
    return detector, generator, hashtag_engine, limiter


def display_header():
    """Display application header."""
    st.markdown('<h1 class="main-header">Social Mood Matcher</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Caption & Hashtag Generator for Social Media</p>', unsafe_allow_html=True)
    st.markdown("---")


def display_sentiment_info(sentiment_result):
    """Display sentiment detection results."""
    st.markdown("### 🎭 Detected Vibe")
    
    sentiment = sentiment_result['sentiment'].capitalize()
    confidence = sentiment_result['confidence']
    
    # Color based on sentiment
    sentiment_colors = {
        "Happy": "#FFD700", "Calm": "#87CEEB", "Cozy": "#FFA07A",
        "Aesthetic": "#DDA0DD", "Adventurous": "#32CD32", "Luxury": "#FFD700",
        "Energetic": "#FF6347", "Peaceful": "#98FB98", "Romantic": "#FF69B4",
        "Nostalgic": "#D2B48C"
    }
    color = sentiment_colors.get(sentiment, "#667eea")
    
    st.markdown(
        f'<div class="sentiment-badge" style="background-color: {color}; color: white;">'
        f'{sentiment} <span class="confidence-score">({confidence:.1%} confidence)</span>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Show category
    st.markdown(f"**Category:** {sentiment_result['category'].capitalize()}")
    
    # Show image description
    with st.expander("📝 AI Image Description"):
        st.write(sentiment_result['caption'])


def display_caption_and_hashtags(caption, hashtags, platform="twitter"):
    """Display generated caption and hashtags with character count."""
    st.markdown("### ✨ Generated Content")
    
    # Caption
    st.markdown('<div class="caption-box">' + caption + '</div>', unsafe_allow_html=True)
    
    # Hashtags
    if hashtags:
        hashtag_string = ' '.join(hashtags) if isinstance(hashtags, list) else hashtags
        st.markdown('<div class="hashtag-box">' + hashtag_string + '</div>', unsafe_allow_html=True)
    
    # Character count
    limiter = get_character_limiter()
    combined_text = combine_caption_and_hashtags(caption, hashtags)
    stats = limiter.get_character_stats(combined_text, platform)
    
    # Determine color based on usage
    if stats['percentage_used'] <= 70:
        char_class = "char-ok"
        icon = "✅"
    elif stats['percentage_used'] <= 90:
        char_class = "char-warning"
        icon = "⚠️"
    else:
        char_class = "char-danger"
        icon = "🚨"
    
    st.markdown(
        f'<div class="char-counter {char_class}">'
        f'{icon} {stats["character_count"]} / {stats["character_limit"]} characters '
        f'({stats["percentage_used"]:.1f}% used)'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Copy to clipboard button
    st.code(combined_text, language=None)
    st.info("💡 Click the copy button above to copy to clipboard!")


def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    
    # Load models
    try:
        detector, generator, hashtag_engine, limiter = load_models()
        st.session_state.models_loaded = True
    except Exception as e:
        st.error(f"❌ Error loading models: {str(e)}")
        st.info("💡 Make sure you have installed all requirements: `pip install -r requirements.txt`")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("## Settings")
        
        # Caption style selection
        st.markdown("### Caption Style")
        selected_style = st.selectbox(
            "Choose your style:",
            options=list(CAPTION_STYLES.keys()),
            format_func=lambda x: x.capitalize(),
            index=list(CAPTION_STYLES.keys()).index(st.session_state.selected_style)
        )
        st.session_state.selected_style = selected_style
        
        # Show style description
        style_info = CAPTION_STYLES[selected_style]
        st.markdown(f"**Tone:** {style_info['tone']}")
        st.markdown(f"**Formality:** {style_info['formality']}")
        
        st.markdown("---")
        
        # Platform selection
        st.markdown("### Platform")
        platform = st.selectbox(
            "Target platform:",
            options=["twitter", "instagram", "facebook"],
            format_func=lambda x: x.capitalize()
        )
        
        st.markdown(f"**Character Limit:** {CHARACTER_LIMITS[platform]}")
        
        st.markdown("---")
        
        # Number of hashtags
        st.markdown("### Hashtags")
        num_hashtags = st.slider(
            "Number of hashtags:",
            min_value=3,
            max_value=10,
            value=6
        )
        
        st.markdown("---")
        
        # AI Model selection
        st.markdown("### AI Model")
        
        # Check if Gemini API key is available
        gemini_available = API_KEYS.get("gemini") is not None
        
        if gemini_available:
            use_gemini = st.toggle(
                "Use Google Gemini API",
                value=st.session_state.use_gemini,
                help="Toggle between local models (BLIP) and Google Gemini API for enhanced analysis"
            )
            st.session_state.use_gemini = use_gemini
            
            if use_gemini:
                st.success("✨ Using Gemini API (Enhanced)")
            else:
                st.info("🔧 Using Local Models (BLIP)")
        else:
            st.warning("⚠️ Gemini API key not configured")
            st.caption("Add GEMINI_API_KEY to .env file to enable Gemini features")
            st.session_state.use_gemini = False
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Social Mood Matcher** uses advanced AI to:
            - 🎭 Detect image sentiment/vibe
            - ✍️ Generate engaging captions
            - #️⃣ Suggest trending hashtags
            - 📏 Ensure character limits
            
            **AI Models:**
            - 🌟 Google Gemini (Enhanced, requires API key)
            - 🔧 BLIP + DistilBERT (Local, no API needed)
            - ✍️ Custom caption templates
            - #️⃣ 2024 trending hashtags
            """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Image")
        uploaded_file = st.file_uploader(
            "Choose an image (scenery or food)",
            type=UI_CONFIG["supported_formats"],
            help=f"Max size: {UI_CONFIG['max_upload_size_mb']}MB"
        )
        
        if uploaded_file:
            # Validate and load image
            image, error = validate_and_load_image(uploaded_file)
            
            if error:
                st.error(f"❌ {error}")
            else:
                # Display image
                st.image(image, caption="Uploaded Image", use_container_width=True)
                
                # Process button
                if st.button("🚀 Generate Caption & Hashtags", type="primary"):
                    with st.spinner("🔮 Analyzing image and generating content..."):
                        try:
                            # Choose AI model based on toggle
                            if st.session_state.use_gemini:
                                if st.session_state.gemini_analyzer is None:
                                    st.session_state.gemini_analyzer = get_gemini_analyzer()
                                
                                gemini = st.session_state.gemini_analyzer
                                if gemini:
                                    # 1. Basic Sentiment Analysis
                                    sentiment_result = gemini.analyze_image_sentiment(image)
                                    st.session_state.sentiment_result = sentiment_result
                                    
                                    if sentiment_result['success']:
                                        # 2. Multi-Variant Captions
                                        variants = gemini.generate_caption_variants(
                                            image=image,
                                            sentiment=sentiment_result['sentiment'],
                                            category=sentiment_result['category']
                                        )
                                        st.session_state.caption_variants = variants
                                        caption = variants.get("aesthetic") or variants.get("punchy")
                                        
                                        # 3. Visual Intelligence (Pro)
                                        st.session_state.visual_analysis = gemini.get_visual_intelligence(image)
                                    else:
                                        st.error("Gemini API error, falling back to local models")
                                        st.session_state.use_gemini = False
                                        sentiment_result = detector.detect_sentiment(image)
                                        caption = generator.generate_caption(
                                            sentiment=sentiment_result['sentiment'],
                                            style=selected_style,
                                            image_caption=sentiment_result['caption'],
                                            category=sentiment_result['category']
                                        )
                            else:
                                # Use local models (Simple Mode)
                                sentiment_result = detector.detect_sentiment(image)
                                st.session_state.sentiment_result = sentiment_result
                                if sentiment_result['success']:
                                    caption = generator.generate_caption(
                                        sentiment=sentiment_result['sentiment'],
                                        style=selected_style,
                                        image_caption=sentiment_result['caption'],
                                        category=sentiment_result['category']
                                    )
                                    st.session_state.caption_variants = {"result": caption}
                                    st.session_state.visual_analysis = None
                                else:
                                    st.error(f"❌ Error: {sentiment_result.get('error', 'Unknown error')}")
                                    caption = None
                            
                            if caption and sentiment_result.get('success'):
                                # Generate hashtags
                                hashtags = hashtag_engine.get_hashtags_by_priority(
                                    category=sentiment_result['category'],
                                    sentiment=sentiment_result['sentiment'],
                                    all_sentiments=sentiment_result.get('all_sentiments', {})
                                )[:num_hashtags]
                                
                                # Apply character limiting
                                hashtag_string = ' '.join(hashtags)
                                limited_caption, limited_hashtags, _ = limiter.limit_text(
                                    caption, hashtag_string, platform
                                )
                                
                                # Store in session state
                                st.session_state.generated_caption = limited_caption
                                st.session_state.generated_hashtags = limited_hashtags
                                
                                # Add to History
                                st.session_state.history.append({
                                    "caption": limited_caption,
                                    "hashtags": limited_hashtags,
                                    "sentiment": sentiment_result['sentiment'],
                                    "timestamp": st.session_state.get("last_run", "Just now")
                                })
                                
                                ai_source = "Google Gemini" if st.session_state.use_gemini else "Local BLIP"
                                st.success(f"✅ Content generated successfully using {ai_source}!")
                                
                        except Exception as e:
                            st.error(f"Error processing image: {str(e)}")

    
    with col2:
        st.markdown("### 📊 AI Results")
        
        tab_basic, tab_pro, tab_history = st.tabs(["✨ Content", "🧠 Visual Pro", "📜 History"])
        
        with tab_basic:
            if st.session_state.sentiment_result and st.session_state.generated_caption:
                display_sentiment_info(st.session_state.sentiment_result)
                
                # Multi-variant selector (if Gemini)
                if st.session_state.use_gemini and st.session_state.caption_variants:
                    st.markdown("#### 🔄 Select Your Variant")
                    v_options = list(st.session_state.caption_variants.keys())
                    selected_v = st.segmented_control(
                        "Choose style:",
                        options=v_options,
                        format_func=lambda x: x.capitalize(),
                        default="aesthetic" if "aesthetic" in v_options else v_options[0]
                    )
                    if selected_v:
                        st.session_state.generated_caption = st.session_state.caption_variants[selected_v]

                display_caption_and_hashtags(
                    st.session_state.generated_caption,
                    st.session_state.generated_hashtags,
                    platform
                )
                
                # Download button
                full_text = f"{st.session_state.generated_caption}\n\n{' '.join(st.session_state.generated_hashtags)}"
                st.download_button(
                    label="💾 Download as Text File",
                    data=full_text,
                    file_name="caption_export.txt",
                    mime="text/plain"
                )
            else:
                st.info("👆 Upload an image and click 'Generate'!")

        with tab_pro:
            if st.session_state.use_gemini and st.session_state.visual_analysis:
                st.markdown("### 🔍 Visual Intelligence Dashboard")
                v = st.session_state.visual_analysis
                
                st.markdown(f"""
                <div class='info-card'>
                    <p>🌈 <b>Dominant Colors:</b> {v.get('colors', 'N/A')}</p>
                    <p>📦 <b>Detected Objects:</b> {v.get('objects', 'N/A')}</p>
                    <p>📸 <b>Composition Tip:</b> <i>{v.get('tip', 'N/A')}</i></p>
                </div>
                """, unsafe_allow_html=True)
            elif not st.session_state.use_gemini:
                st.warning("🚀 Visual Intelligence requires Gemini Mode. Toggle it in the sidebar!")
            else:
                st.info("Waiting for analysis...")

        with tab_history:
            if st.session_state.history:
                st.markdown("### Recent Generations")
                for i, item in enumerate(reversed(st.session_state.history[-5:])):
                    with st.expander(f"Generation #{len(st.session_state.history)-i} ({item['sentiment']})"):
                        st.write(item['caption'])
                        st.caption(" ".join(item['hashtags']))
            else:
                st.write("No history yet.")

    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666; font-size: 0.9rem;">'
        'Made with ❤️ using Streamlit & Hugging Face Transformers | '
        '© 2024 Social Mood Matcher'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
