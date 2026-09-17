import React from 'react';

const SocialMediaCalendar = ({ data, productName, category, demographic }) => {
  // No data to display
  if (!data || !data.dates || !data.base_trend) {
    return null;
  }

  // Extract data needed for the calendar
  const dates = data.dates || [];
  const baseTrend = data.base_trend || [];
  
  // Find peak days (top 25% of the trend values)
  const sortedTrendValues = [...baseTrend].sort((a, b) => b - a);
  const peakThreshold = sortedTrendValues[Math.floor(sortedTrendValues.length * 0.25)];
  
  // Map dates to their trend values and identify peak days
  const trendByDate = dates.map((date, index) => ({
    date,
    trend: baseTrend[index],
    isPeak: baseTrend[index] >= peakThreshold
  }));

  // Social media platforms based on demographics
  const getPlatformsForDemographic = (demographic) => {
    const platformMap = {
      'Young Adults': ['Instagram', 'TikTok', 'YouTube'],
      'Professionals': ['LinkedIn', 'Twitter', 'Facebook'],
      'Parents': ['Facebook', 'Pinterest', 'Instagram'],
      'Seniors': ['Facebook', 'YouTube', 'Pinterest'],
      'Teenagers': ['TikTok', 'Instagram', 'Snapchat'],
      'Children': ['YouTube Kids', 'TikTok (monitored)', 'Supervised Instagram'],
      'Men': ['Twitter', 'Reddit', 'YouTube'],
      'Women': ['Instagram', 'Pinterest', 'Facebook'],
      'Families': ['Facebook', 'YouTube', 'Instagram'],
      'Students': ['Instagram', 'TikTok', 'Discord']
    };
    
    return platformMap[demographic] || ['Instagram', 'Facebook', 'Twitter'];
  };

  // Content types based on category
  const getContentTypesForCategory = (category) => {
    const contentMap = {
      'Clothing': ['Product showcase', 'Style tips', 'Outfit of the day'],
      'Electronics': ['Unboxing', 'How-to tutorial', 'Feature spotlight'],
      'Home Decor': ['Styling tips', 'Before & after', 'DIY ideas'],
      'Beauty': ['Tutorial', 'Before & after', 'Product review'],
      'Health': ['Educational content', 'Testimonial', 'Tips & tricks'],
      'Fitness': ['Workout demo', 'Success story', 'Challenge'],
      'Kitchen': ['Recipe', 'Product demo', 'Kitchen hack'],
      'Office': ['Productivity tip', 'Setup showcase', 'How-to guide'],
      'Outdoors': ['Adventure content', 'Product in action', 'Tips & tricks'],
      'Pet Supplies': ['Cute pet content', 'How-to guide', 'Product demo'],
      'Food & Beverage': ['Recipe', 'Tasting', 'Behind the scenes'],
      'Toys': ['Play ideas', 'Educational benefits', 'Unboxing'],
      'Books': ['Review', 'Author spotlight', 'Reading excerpt'],
      'Art Supplies': ['Tutorial', 'Inspiration', 'Showcase'],
      'Handmade': ['Making process', 'Inspiration', 'Product story']
    };
    
    return contentMap[category] || ['Product showcase', 'How-to', 'Behind the scenes'];
  };

  // Get platforms and content types for this product
  const platforms = getPlatformsForDemographic(demographic);
  const contentTypes = getContentTypesForCategory(category);

  // Generate post recommendations 
  const generatePostRecommendations = (trendData) => {
    const recommendations = [];
    
    // Pre-launch posts (first 20% of timeline)
    const prelaunchEndIndex = Math.floor(trendData.length * 0.2);
    
    for (let i = 0; i < prelaunchEndIndex; i++) {
      if (i % 3 === 0) { // Create a post every third day during pre-launch
        recommendations.push({
          date: trendData[i].date,
          phase: 'Pre-launch',
          platforms: i % 2 === 0 ? [platforms[0]] : [platforms[1]], 
          content: 'Teaser content',
          contentType: 'Coming soon',
          isPeak: false,
          sample: `Exciting news! Our new ${productName} is coming soon. Stay tuned! #ComingSoon #${category.replace(/[^a-zA-Z0-9]/g, '')}`
        });
      }
    }
    
    // Launch day (post exactly at 20% mark)
    recommendations.push({
      date: trendData[prelaunchEndIndex].date,
      phase: 'Launch',
      platforms: platforms,
      content: 'Product launch announcement',
      contentType: 'Announcement',
      isPeak: true,
      sample: `🎉 Our ${productName} is now available! [Link] Check it out now and be among the first to experience it! #ProductLaunch #${category.replace(/[^a-zA-Z0-9]/g, '')}`
    });
    
    // Post-launch (remaining days)
    for (let i = prelaunchEndIndex + 1; i < trendData.length; i++) {
      const item = trendData[i];
      
      // Post more frequently on peak days
      if (item.isPeak || i % 4 === 0) {
        const contentTypeIndex = (i % contentTypes.length);
        const platformIndex = (i % platforms.length);
        
        let postType = '';
        let samplePost = '';
        
        if (item.isPeak) {
          postType = 'Peak engagement content';
          samplePost = `Don't miss out! Our ${productName} is perfect for ${contentTypes[contentTypeIndex].toLowerCase()}. [Link] #${productName.replace(/\s+/g, '')} #${category.replace(/[^a-zA-Z0-9]/g, '')}`;
        } else {
          postType = 'Regular engagement';
          samplePost = `Here's how our ${productName} can help with ${contentTypes[contentTypeIndex].toLowerCase()}. #${category.replace(/[^a-zA-Z0-9]/g, '')} #ProductTips`;
        }
        
        recommendations.push({
          date: item.date,
          phase: 'Post-launch',
          platforms: [platforms[platformIndex]],
          content: postType,
          contentType: contentTypes[contentTypeIndex],
          isPeak: item.isPeak,
          sample: samplePost
        });
      }
    }
    
    return recommendations;
  };

  const postRecommendations = generatePostRecommendations(trendByDate);

  return (
    <div className="mt-8">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Social Media Launch Calendar</h3>
      <p className="text-sm text-gray-500 mb-4">
        Based on your predicted trend, here's a suggested social media posting schedule to maximize your product launch impact.
      </p>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phase</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Content Type</th>
              <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sample Post</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {postRecommendations.map((post, index) => (
              <tr key={index} className={post.isPeak ? "bg-indigo-50" : ""}>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">{post.date.split(' ')[0]}</td>
                <td className="px-4 py-3 whitespace-nowrap text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    post.phase === 'Pre-launch' 
                      ? 'bg-yellow-100 text-yellow-800' 
                      : post.phase === 'Launch' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                  }`}>
                    {post.phase}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {post.platforms.join(', ')}
                </td>
                <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {post.contentType}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 max-w-xs truncate">
                  <div className="group relative">
                    <p className="truncate">{post.sample}</p>
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 absolute z-10 -mt-8 ml-6 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg">
                      {post.sample}
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 text-sm mb-2">Recommended Platforms</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {platforms.map((platform, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-indigo-500 mr-2"></span>
                {platform}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 text-sm mb-2">Content Strategy</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {contentTypes.map((type, index) => (
              <li key={index} className="flex items-center">
                <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                {type}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
          <h4 className="font-medium text-gray-900 text-sm mb-2">Best Practices</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li className="flex items-center">
              <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
              Post consistently on peak days
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
              Use high-quality visuals
            </li>
            <li className="flex items-center">
              <span className="w-2 h-2 rounded-full bg-yellow-500 mr-2"></span>
              Include clear call-to-actions
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SocialMediaCalendar;
