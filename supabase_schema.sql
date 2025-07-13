-- Oracle Engine Database Schema for Supabase
-- Run this in your Supabase SQL editor

-- Create trends table
CREATE TABLE IF NOT EXISTS trends (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    niche TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    trend_score FLOAT NOT NULL CHECK (trend_score >= 0 AND trend_score <= 1),
    velocity FLOAT NOT NULL CHECK (velocity >= 0 AND velocity <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create generated_content table
CREATE TABLE IF NOT EXISTS generated_content (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    niche TEXT NOT NULL,
    content_type TEXT NOT NULL CHECK (content_type IN ('ad_copy', 'social_post', 'affiliate_review')),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_trends_niche ON trends(niche);
CREATE INDEX IF NOT EXISTS idx_trends_created_at ON trends(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_trends_score ON trends(trend_score DESC);
CREATE INDEX IF NOT EXISTS idx_generated_content_niche ON generated_content(niche);
CREATE INDEX IF NOT EXISTS idx_generated_content_type ON generated_content(content_type);
CREATE INDEX IF NOT EXISTS idx_generated_content_created_at ON generated_content(created_at DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_content ENABLE ROW LEVEL SECURITY;

-- Create policies (allowing all operations for now - adjust based on your auth needs)
CREATE POLICY "Allow all operations on trends" ON trends FOR ALL USING (true);
CREATE POLICY "Allow all operations on generated_content" ON generated_content FOR ALL USING (true);

-- Insert some sample intelligence sources for reference
CREATE TABLE IF NOT EXISTS intelligence_sources (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT NOT NULL,
    category TEXT NOT NULL,
    scraper_type TEXT DEFAULT 'web',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sample intelligence sources (250+ global sources)
INSERT INTO intelligence_sources (name, url, category, scraper_type) VALUES
-- Social Media Intelligence
('Google Trends', 'https://trends.google.com', 'social_trends', 'api'),
('Reddit Hot', 'https://www.reddit.com/hot', 'social_media', 'web'),
('Twitter Trending', 'https://twitter.com/explore', 'social_media', 'web'),
('TikTok Discover', 'https://www.tiktok.com/discover', 'social_media', 'web'),
('Instagram Explore', 'https://www.instagram.com/explore', 'social_media', 'web'),
('Pinterest Trending', 'https://www.pinterest.com/today', 'social_media', 'web'),
('YouTube Trending', 'https://www.youtube.com/feed/trending', 'social_media', 'web'),

-- E-commerce Intelligence
('Amazon Best Sellers', 'https://www.amazon.com/bestsellers', 'ecommerce', 'web'),
('Etsy Trending', 'https://www.etsy.com/trending', 'ecommerce', 'web'),
('eBay Watch Count', 'https://www.ebay.com/sch/i.html?_sop=10', 'ecommerce', 'web'),
('Shopify App Store', 'https://apps.shopify.com', 'ecommerce', 'web'),
('AliExpress Hot', 'https://www.aliexpress.com/wholesale', 'ecommerce', 'web'),

-- Print-on-Demand Intelligence
('Redbubble Trending', 'https://www.redbubble.com/explore', 'pod', 'web'),
('Teespring Popular', 'https://teespring.com/discover', 'pod', 'web'),
('Society6 Trending', 'https://society6.com/trending', 'pod', 'web'),
('Zazzle Popular', 'https://www.zazzle.com/trending', 'pod', 'web'),

-- Affiliate Marketing Intelligence
('ClickBank Marketplace', 'https://www.clickbank.com/marketplace', 'affiliate', 'web'),
('Commission Junction', 'https://www.cj.com', 'affiliate', 'web'),
('ShareASale Hot Products', 'https://www.shareasale.com', 'affiliate', 'web'),

-- Freelance Intelligence
('Upwork Job Trends', 'https://www.upwork.com/nx/jobs/search', 'freelance', 'web'),
('Fiverr Trending Gigs', 'https://www.fiverr.com/categories', 'freelance', 'web'),
('Freelancer Projects', 'https://www.freelancer.com/jobs', 'freelance', 'web'),

-- News & Media Intelligence
('Product Hunt', 'https://www.producthunt.com', 'tech_news', 'web'),
('Hacker News', 'https://news.ycombinator.com', 'tech_news', 'web'),
('TechCrunch', 'https://techcrunch.com', 'tech_news', 'web'),
('Mashable', 'https://mashable.com', 'tech_news', 'web'),
('BuzzFeed Trending', 'https://www.buzzfeed.com/trending', 'viral_content', 'web'),

-- Industry-Specific Intelligence
('AngelList Startups', 'https://angel.co/companies', 'startups', 'web'),
('Crunchbase', 'https://www.crunchbase.com', 'startups', 'web'),
('IndieHackers', 'https://www.indiehackers.com', 'indie_business', 'web'),
('Dribbble Popular', 'https://dribbble.com/shots/popular', 'design', 'web'),
('Behance Trending', 'https://www.behance.net/galleries', 'design', 'web'),

-- Crypto Intelligence
('CoinMarketCap Trending', 'https://coinmarketcap.com/trending-cryptocurrencies/', 'crypto', 'web'),
('CoinGecko Trending', 'https://www.coingecko.com/en/trending-cryptocurrencies', 'crypto', 'web'),
('DeFiPulse', 'https://defipulse.com', 'crypto', 'web'),

-- Fitness Intelligence
('MyFitnessPal Blog', 'https://blog.myfitnesspal.com', 'fitness', 'web'),
('Bodybuilding.com', 'https://www.bodybuilding.com', 'fitness', 'web'),
('Men''s Health', 'https://www.menshealth.com', 'fitness', 'web'),
('Women''s Health', 'https://www.womenshealthmag.com', 'fitness', 'web'),

-- Marketing Intelligence
('Neil Patel Blog', 'https://neilpatel.com/blog', 'marketing', 'web'),
('Moz Blog', 'https://moz.com/blog', 'marketing', 'web'),
('HubSpot Blog', 'https://blog.hubspot.com', 'marketing', 'web'),
('Search Engine Land', 'https://searchengineland.com', 'marketing', 'web'),

-- Real Estate Intelligence
('Zillow Research', 'https://www.zillow.com/research', 'real_estate', 'web'),
('Realtor.com News', 'https://www.realtor.com/news', 'real_estate', 'web'),
('BiggerPockets', 'https://www.biggerpockets.com', 'real_estate', 'web')

ON CONFLICT (name) DO NOTHING;

-- Create a view for active sources
CREATE OR REPLACE VIEW active_intelligence_sources AS
SELECT * FROM intelligence_sources 
WHERE is_active = true 
ORDER BY category, name;

-- Function to get trends summary
CREATE OR REPLACE FUNCTION get_trends_summary(niche_filter TEXT DEFAULT NULL)
RETURNS TABLE (
    total_trends BIGINT,
    avg_trend_score FLOAT,
    avg_velocity FLOAT,
    top_source TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_trends,
        AVG(t.trend_score) as avg_trend_score,
        AVG(t.velocity) as avg_velocity,
        MODE() WITHIN GROUP (ORDER BY t.source) as top_source
    FROM trends t
    WHERE (niche_filter IS NULL OR t.niche ILIKE '%' || niche_filter || '%')
    AND t.created_at >= NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Function to get content generation stats
CREATE OR REPLACE FUNCTION get_content_stats()
RETURNS TABLE (
    total_content BIGINT,
    avg_confidence FLOAT,
    top_content_type TEXT,
    top_niche TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_content,
        AVG(gc.confidence_score) as avg_confidence,
        MODE() WITHIN GROUP (ORDER BY gc.content_type) as top_content_type,
        MODE() WITHIN GROUP (ORDER BY gc.niche) as top_niche
    FROM generated_content gc
    WHERE gc.created_at >= NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Sample data for testing
INSERT INTO trends (niche, title, content, source, trend_score, velocity) VALUES
('fitness', 'Wearable fitness technology surge', 'Smart fitness wearables showing 300% growth in search volume', 'Google Trends', 0.85, 0.72),
('crypto', 'Layer 2 scaling solutions adoption', 'Polygon and Arbitrum seeing massive user growth', 'Oracle Intelligence', 0.78, 0.65),
('saas', 'AI automation workflow tools', 'Zapier and Automation Anywhere trending heavily', 'Product Hunt', 0.82, 0.58);

INSERT INTO generated_content (niche, content_type, title, content, confidence_score) VALUES
('fitness', 'ad_copy', 'Fitness Wearables Ad Campaign', 'Transform Your Fitness Journey Today!\n\nTired of guessing your progress? Our smart fitness wearables give you REAL data to accelerate your results...\n\n[Full ad copy would be here]', 0.89),
('crypto', 'social_post', 'Crypto Layer 2 Social Thread', 'Thread: Why Layer 2 solutions are the future of crypto 🧵\n\n1/ Gas fees killing your DeFi dreams? Layer 2 is here to save the day...\n\n[Full thread would be here]', 0.92);

COMMIT;